import random
import string

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from loguru import logger

from dndserver import database
from dndserver.protos import Account_pb2 as acc


def process_login(self, data: bytes):
    req = acc.SC2S_ACCOUNT_LOGIN_REQ()
    req.ParseFromString(data[8:])
    logger.debug(f"Received SC2S_ACCOUNT_LOGIN_REQ:\n {req}")

    # Attempt to get the user requested and register an account if necessary
    user = get_user(req.loginId)
    if not user:
        # TODO: Implement secret key generation prompt
        register_user(
            username=req.loginId, password=req.password, ip_address=self.transport.client[0], hwids=req.hwIds[0],
            build_version=req.buildVersion
        )
        user = get_user(req.loginId)

    res = acc.SS2C_ACCOUNT_LOGIN_RES()
    # Return FAIL_SHORT_ID_OR_PASSWORD on too short username/password
    if len(req.loginId) <= 2 or len(req.password) <= 2:
        res.Result = 5
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res.SerializeToString()

    # Return FAIL_OVERFLOW_ID_OR_PASSWORD on too long username
    # Not sure if there's a password overflow limit because the
    # password field starts glitching out when you add too many
    # characters.
    if len(req.loginId) > 20:
        res.Result = 6
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res.SerializeToString()

    # Return FAIL_PASSWORD on mismatching password
    try:
        PasswordHasher().verify(user["password"], req.password)
    except VerifyMismatchError:
        res.Result = 3
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res.SerializeToString()

    # Returns the respective SS2C_ACCOUNT_LOGIN_RES *__BAN_USER ban enum.
    if user["is_banned"]:
        res.Result = user["is_banned"]
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        res.AccountInfo.CopyFrom(account_info)
        return res.SerializeToString()

    res = acc.SS2C_ACCOUNT_LOGIN_RES()
    res.accountId = "1"
    res.serverLocation = 1
    res.secretToken = ''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
    # res.sessionId = "session123"     # TODO: Figure out how session IDs look
    # res.isReconnect = False          # TODO: Need to maintain user states and connection statuses?

    account_info = acc.SLOGIN_ACCOUNT_INFO()
    account_info.AccountID = "1"  # str(user["id"])
    res.AccountInfo.CopyFrom(account_info)

    return res.SerializeToString()


def register_user(username: str, password: str, hwids: str, build_version: str, ip_address: str):
    db = database.get()
    user = db["users"].insert(dict(
        username=username,
        password=PasswordHasher().hash(password),
        hwids=hwids,
        build_version=build_version,
        ip_address=ip_address
    ))
    db.commit()
    db.close()
    return user


def get_user(username: str):
    db = database.get()
    user = db["users"].find_one(username=username)
    return user if user else False
