import random
import string

import argon2
import arrow

from dndserver.database import db
from dndserver.models import Hwid, Account
from dndserver.persistent import sessions
from dndserver.protos.Account import SC2S_ACCOUNT_LOGIN_REQ, SLOGIN_ACCOUNT_INFO, SS2C_ACCOUNT_LOGIN_RES
from dndserver.protos.Common import SS2C_SERVICE_POLICY_NOT, FSERVICE_POLICY


def process_login(ctx, msg) -> SS2C_ACCOUNT_LOGIN_RES:
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

        res.secretToken = account.secret_token

    # Check if an hwId is associated to an account_id, if not add to db
    for hwid in req.hwIds:
        if not db.query(Hwid).filter_by(hwid=hwid).filter_by(account_id=account.id).first():
            hwid = Hwid(account_id=account.id, hwid=hwid, seen_at=arrow.utcnow())
            hwid.save()

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

    service_policy_notification(ctx)

    return res


def service_policy_notification(ctx) -> None:
    # Fix for Ante (High-Roller Entrance Fee)
    # Policy Type '7' referes to High-Roller
    # There's a lot more policy types, all with values, still unknown what each type does.
    # and therefore will not implement the rest yet.
    policy = [FSERVICE_POLICY(policyType=7, policyValue=100)]

    notify = SS2C_SERVICE_POLICY_NOT(policyList=policy)
    ctx.reply(notify)


def kick_concurrent_user(newly_connected_account) -> None:
    """Searches for already connected account and kicks if a match is found."""
    for transport, user in sessions.items():
        # case where a duplicate account is found
        if user.account == newly_connected_account:
            transport.loseConnection()
            break
