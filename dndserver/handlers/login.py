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

    # TODO: Add check to make sure people don't spoof requests for <=2 character
    # names, passwords are hash when we're receiving them so we don't need to
    # worry about that

    user = get_user(req.loginId)
    if not user:
        # TODO: Implement secret key generation prompt
        register_user(
            username=req.loginId, password=req.password, ip_address=self.transport.client[0], hwids=req.hwIds[0],
            build_version=req.buildVersion
        )
        user = get_user(req.loginId)

    resp = account.SS2C_ACCOUNT_LOGIN_RES()

    # Returns FAIL_PASSWORD on mismatching password
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
