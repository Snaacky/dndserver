import random
import string

import argon2
from datetime import datetime
from dndserver.database import db
from dndserver.models import Account, Hwid
from dndserver.protos.Account import SLOGIN_ACCOUNT_INFO, SS2C_ACCOUNT_LOGIN_RES, SC2S_ACCOUNT_LOGIN_REQ
from dndserver.sessions import sessions
from sqlalchemy.orm import Session

def is_banned_hwid(hwid: str, session: Session) -> bool:
    banned_hwid = session.query(Hwid).filter_by(hwid=hwid, is_banned=True).first()
    return banned_hwid is not None

def add_hwid_to_user(user_id: int, hwid: str, session: Session):
    hwid_entry = Hwid(user_id=user_id, hwid=hwid, seen_at=datetime.now())
    session.add(hwid_entry)
    session.commit()
    
def hwid_already_logged(user_id: int, hwid: str, session: Session) -> bool:
    existing_hwid = session.query(Hwid).filter_by(user_id=user_id, hwid=hwid).first()
    return existing_hwid is not None

def process_login(ctx, msg):
    """Occurs when the user attempts to login to the game server."""
    req = SC2S_ACCOUNT_LOGIN_REQ()
    req.ParseFromString(msg)

    # TODO: Not all SS2C_ACCOUNT_LOGIN_RES fields are implemented.
    res = SS2C_ACCOUNT_LOGIN_RES(serverLocation=1)

    user = db.query(Account).filter_by(username=req.loginId).first()

    # Check if the HWID is banned
    if is_banned_hwid(req.hwIds[0], db):
        res.Result = res.FAIL_PASSWORD
        return res
    
    if not user:
        user = Account(
            username=req.loginId,
            password=argon2.PasswordHasher().hash(req.password),
            secret_token=''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
        )
        user.save()

        add_hwid_to_user(user.id, req.hwIds[0], db)  
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

    # Log HWID for the user after successful password verification
    # if the combination of user_id and hwid doesn't already exist in the table
    if not hwid_already_logged(user.id, req.hwIds[0], db):
        add_hwid_to_user(user.id, req.hwIds[0], db)

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
