import random
import string

import argon2

from dndserver.database import db
from dndserver.models import Account
from dndserver.protos.Account import SLOGIN_ACCOUNT_INFO, SS2C_ACCOUNT_LOGIN_RES, SC2S_ACCOUNT_LOGIN_REQ
from dndserver.sessions import sessions


def process_login(ctx, msg):
    """Occurs when the user attempts to login to the game server."""
    req = SC2S_ACCOUNT_LOGIN_REQ()
    req.ParseFromString(msg)

    # TODO: Not all SS2C_ACCOUNT_LOGIN_RES fields are implemented.
    res = SS2C_ACCOUNT_LOGIN_RES(serverLocation=1)

    user = db.query(Account).filter_by(username=req.loginId).first()
    if not user:
        user = Account(
            username=req.loginId,
            password=argon2.PasswordHasher().hash(req.password),
            secret_token=''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
        )
        user.save()

        # TODO: Create new hwid objects and save them to the db here
        res.secretToken = user.secret_token

    # Return FAIL_SHORT_ID_OR_PASSWORD on too short username/password.
    if len(req.loginId) <= 2 or len(req.password) <= 2:
        res.Result = res.FAIL_SHORT_ID_OR_PASSWORD
        return res

    # Return FAIL_OVERFLOW_ID_OR_PASSWORD on too long username.
    if len(req.loginId) > 20:
        res.Result = res.FAIL_OVERFLOW_ID_OR_PASSWORD
        return res

    # Return FAIL_PASSWORD on invalid password.
    try:
        argon2.PasswordHasher().verify(user.password, req.password)
    except argon2.exceptions.VerifyMismatchError:
        res.Result = res.FAIL_PASSWORD
        return res

    # Returns the respective SS2C_ACCOUNT_LOGIN_RES *__BAN_USER ban enum.
    if user.ban_type:
        res.Result = user.ban_type
        return res

    res.accountId = str(user.id)
    info = SLOGIN_ACCOUNT_INFO(AccountID=str(user.id))
    res.AccountInfo.CopyFrom(info)

    # Set the user object in session to indicate authentication and for further access.
    sessions[ctx.transport]["user"] = user

    return res

def get_username_from_request(raw_request: bytes) -> str:
    req = SC2S_ACCOUNT_LOGIN_REQ()
    req.ParseFromString(raw_request)
    return req.loginId