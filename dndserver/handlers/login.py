import random
import string

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from loguru import logger

from dndserver import database
from dndserver.protos import Account_pb2 as account


def process_login(self, data: bytes):
    req = account.SC2S_ACCOUNT_LOGIN_REQ()
    req.ParseFromString(data[8:])
    logger.debug(req)

    # Attempt to get the user requested and register an account if necessary
    user = get_user(req.loginId)
    if not user:
        # TODO: Implement secret key generation prompt
        register_user(
            username=req.loginId, password=req.password, ip_address=self.transport.client[0], hwids=req.hwIds[0],
            build_version=req.buildVersion
        )
        user = get_user(req.loginId)

    resp = account.SS2C_ACCOUNT_LOGIN_RES()

    # Return FAIL_SHORT_ID_OR_PASSWORD on too short username/password
    if len(req.loginId) <= 2 or len(req.password) <= 2:
        resp.Result = 5
        account_info = account.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        resp.AccountInfo.CopyFrom(account_info)
        return resp.SerializeToString()

    # Return FAIL_OVERFLOW_ID_OR_PASSWORD on too long username
    # Not sure if there's a password overflow limit because the
    # password field starts glitching out when you add too many
    # characters.
    if len(req.loginId) > 20:
        resp.Result = 6
        account_info = account.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        resp.AccountInfo.CopyFrom(account_info)
        return resp.SerializeToString()

    # Return FAIL_PASSWORD on mismatching password
    try:
        PasswordHasher().verify(user["password"], req.password)
    except VerifyMismatchError:
        resp.Result = 3
        account_info = account.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        resp.AccountInfo.CopyFrom(account_info)
        return resp.SerializeToString()

    # Returns the respective SS2C_ACCOUNT_LOGIN_RES *__BAN_USER ban enum.
    if user["is_banned"]:
        resp.Result = user["is_banned"]
        account_info = account.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = str(user["id"])
        resp.AccountInfo.CopyFrom(account_info)
        return resp.SerializeToString()

    resp.sessionId = "session123"     # TODO: Figure out how session IDs look
    resp.accountId = str(user["id"])  # TODO: Figure out how account IDs look
    resp.secretToken = ''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
    resp.serverLocation = 1
    resp.isReconnect = False          # TODO: Need to maintain user states and connection statuses?

    account_info = account.SLOGIN_ACCOUNT_INFO()
    account_info.AccountID = str(user["id"])
    resp.AccountInfo.CopyFrom(account_info)

    account_info = acc.SLOGIN_ACCOUNT_INFO()
    account_info.AccountID = str(user["id"])
    res.AccountInfo.CopyFrom(account_info)
    return resp.SerializeToString()


def register_user(username: str, password: str, hwids: str, build_version: str, ip_address: str):
    db = database.get()
    user = db["users"].insert(dict(
        username=username,
        password=PasswordHasher().hash(password),
        hwids=hwids,
        build_version=build_version,
        ip_address=ip_address
    ))
    return user


def get_user(username: str):
    db = database.get()
    user = db["users"].find_one(username=username)
    return user if user else False
