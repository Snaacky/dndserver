import random
import string

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from dndserver import database
from dndserver.protos import Account_pb2 as acc


def process_login(self, req):
    """Communication that occurs when the user attempts to login to
    the game server."""
    # Attempt to find the request username in the database.
    user = get_user(req.loginId)
    if not user:
        register_user(  # Register the user instead if it doesn't already exist.
            username=req.loginId, password=req.password, ip_address=self.transport.client[0], hwids=req.hwIds[0],
            build_version=req.buildVersion
        )
        user = get_user(req.loginId)

    res = acc.SS2C_ACCOUNT_LOGIN_RES()

    # Return FAIL_SHORT_ID_OR_PASSWORD on too short username/password.
    if len(req.loginId) <= 2 or len(req.password) <= 2:
        res.Result = 5
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res

    # Return FAIL_OVERFLOW_ID_OR_PASSWORD on too long username.
    if len(req.loginId) > 20:
        res.Result = 6
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res

    # Return FAIL_PASSWORD on invalid password.
    try:
        PasswordHasher().verify(user["password"], req.password)
    except VerifyMismatchError:
        res.Result = 3
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res

    # Returns the respective SS2C_ACCOUNT_LOGIN_RES *__BAN_USER ban enum.
    if user["is_banned"]:
        res.Result = user["is_banned"]
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res

    res = acc.SS2C_ACCOUNT_LOGIN_RES()
    res.accountId = str(user["id"])
    res.serverLocation = 1
    # res.sessionId = "session123"  # TODO: Figure out how session IDs look
    # res.isReconnect = False       # TODO: Need to maintain user states and connection statuses?

    # Generate, save, and show the user a secret token if a registration is occurring.
    if not user["secret_token"]:
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
        res.secretToken = token
        db = database.get()
        db["users"].update(dict(id=user["id"], secret_token=token), ["id"])
        db.commit()
        db.close()

    account_info = acc.SLOGIN_ACCOUNT_INFO()
    account_info.AccountID = str(user["id"])
    res.AccountInfo.CopyFrom(account_info)

    # Set the users ID in the session so future calls know that they're authenticated. 
    self.sessions[self.transport]["accountId"] = user["id"]
    return res


def register_user(username: str, password: str, hwids: str, build_version: str, ip_address: str):
    """Return user object after inserting user into database"""
    db = database.get()
    user = db["users"].insert(dict(
        username=username,
        password=PasswordHasher().hash(password),
        hwids=hwids,
        build_version=build_version,
        is_banned=None,
        ip_address=ip_address,
        secret_token=None
    ))
    db.commit()
    db.close()
    return user


def get_user(username: str):
    """Return user object from database, returns False if non-existent."""
    db = database.get()
    user = db["users"].find_one(username=username)
    return user if user else False
