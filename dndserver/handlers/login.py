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

    # Return FAIL_SHORT_ID_OR_PASSWORD on too short username/password.
    if len(req.loginId) <= 2 or len(req.password) <= 2:
        res.Result = res.FAIL_SHORT_ID_OR_PASSWORD
        return res

    # Return FAIL_OVERFLOW_ID_OR_PASSWORD on too long username.
    if len(req.loginId) > 20:
        res.Result = res.FAIL_OVERFLOW_ID_OR_PASSWORD
        return res

    account = db.query(Account).filter(Account.username.ilike(req.loginId)).first()
    if not account:
        account = Account(
            username=req.loginId,
            password=argon2.PasswordHasher().hash(req.password),
            secret_token="".join(random.choices(string.ascii_uppercase + string.digits, k=21)),
        )
        account.save()

        # TODO: Create new hwid objects and save them to the db here
        res.secretToken = account.secret_token

    # Return FAIL_PASSWORD on invalid password.
    try:
        argon2.PasswordHasher().verify(account.password, req.password)
    except argon2.exceptions.VerifyMismatchError:
        res.Result = res.FAIL_PASSWORD
        return res

    # Returns the respective SS2C_ACCOUNT_LOGIN_RES *__BAN_USER ban enum.
    if account.ban_type:
        res.Result = account.ban_type
        return res

    res.accountId = str(account.id)
    info = SLOGIN_ACCOUNT_INFO(AccountID=str(account.id))
    res.AccountInfo.CopyFrom(info)

    kick_concurrent_user(account)

    sessions[ctx.transport].account = account

    return res


def kick_concurrent_user(newly_connected_account):
    """Searches for already connected account and kicks if a match is found."""
    for transport, user in sessions.items():
        # case where a duplicate account is found
        if user.account == newly_connected_account:
            transport.loseConnection()
            break
