import random
import string
from typing import Union, Dict

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from loguru import logger

from dndserver import database
from dndserver.protos import Account_pb2 as acc


# Check if the given hwid is associated with a banned user
def is_banned_hwid(hwid):
    with database.get() as db:
        user_hwid = db['hwids'].find_one(hwid=hwid)
        if user_hwid:
            banned_user = db['users'].find_one(id=user_hwid['user_id'], is_banned={"not": None})
            return banned_user is not None
        return False

# Get a user by their username
def get_user(username: str) -> Union[Dict, None]:
    """
    Return user object from the database, returns None if non-existent.
    """
    with database.get() as db:
        user = db["users"].find_one(username=username)
    return user if user else None

# Process login requests and respond accordingly
def process_login(self, data: bytes):
    # Deserialize the incoming data
    req = acc.SC2S_ACCOUNT_LOGIN_REQ()

    # Add debug statements to print the incoming data and length
    logger.debug(f"Data received: {data}")
    logger.debug(f"Data length: {len(data)}")

    req.ParseFromString(bytes(data[8:]))

    # If the HWID is associated with a banned user, return an error
    if is_banned_hwid(req.hwIds[0]):
        logger.debug(f"Banned user with HWID {req.hwIds[0]} tried to create a new account")
        res = acc.SS2C_ACCOUNT_LOGIN_RES()
        res.Result = acc.SS2C_ACCOUNT_LOGIN_RES.RESULT.FAIL_PASSWORD
        self.transport.write(res.SerializeToString())
        return res.SerializeToString()

    # Attempt to get the user requested and register an account if necessary
    user = get_user(req.loginId)
    logger.debug(f"User: {user}")
    res = acc.SS2C_ACCOUNT_LOGIN_RES()

    # If the user does not exist, register a new user
    if user is None:
        user = register_user(
            username=req.loginId, password=req.password, ip_address=self.transport.client[0], hwid=req.hwIds[0],
            build_version=req.buildVersion
        )
    elif not PasswordHasher().verify(user["password"], req.password) or user['is_banned']:
        res.Result = acc.SS2C_ACCOUNT_LOGIN_RES.RESULT.FAIL_PASSWORD
        self.transport.write(res.SerializeToString())
        return res.SerializeToString()
    else:
        # Check if the HWID exists for the user, add it if not
        hwid = get_hwid(user["id"], req.hwIds[0])
        if not hwid:
            add_hwid(user["id"], req.hwIds[0])

    # Set response parameters
    res.accountId = str(user["id"])
    res.serverLocation = 1
    res.secretToken = ''.join(random.choices(string.ascii_uppercase + string.digits, k=21))

    # Update the secret token if not already set
    if not user["secret_token"]:
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
        res.secretToken = token
        db = database.get()
        db["users"].update(dict(id=user["id"], secret_token=token), ["id"])
        db.commit()
        db.close()

    # Set account information in response
    account_info = acc.SLOGIN_ACCOUNT_INFO()
    account_info.AccountID = str(user["id"])
    res.AccountInfo.CopyFrom(account_info)

    return res.SerializeToString()  # Return the serialized response

# Register a new user and store their initial HWID
def register_user(username: str, password: str, hwid: str, build_version: str, ip_address: str) -> Union[Dict, None]:
    """
    Register a new user and store their initial HWID.
    Returns the newly created user object, or None if the user already exists.
    """
    with database.get() as db:
        # Check if a user with the same username already exists
        existing_user = db["users"].find_one(username=username)
        if existing_user:
            return None
        
        user_id = db["users"].insert(dict(
            username=username,
            password=PasswordHasher().hash(password),
            build_version=build_version,
            is_banned=None,
            ip_address=ip_address,
            secret_token=None
        ))
        db.commit()
        user = db["users"].find_one(id=user_id)

    # Add the initial HWID for the user
    add_hwid(user["id"], hwid)

    return user

# Add a new HWID for a user
def add_hwid(user_id: int, hwid: str) -> None:
    """Add a new HWID for a user."""
    with database.get() as db:
        db["hwids"].insert(dict(user_id=user_id, hwid=hwid))
        db.commit()

# Check if a specific HWID exists for a user
def get_hwid(user_id: int, hwid: str) -> Union[Dict, bool]:
    """
    Check if a specific HWID exists for a user.
    Returns the HWID entry if found, False otherwise.
    """
    with database.get() as db:
        hwid_entry = db["hwids"].find_one(user_id=user_id, hwid=hwid)
    return hwid_entry if hwid_entry else False

# Get a user by their username
def get_user(username: str) -> Union[Dict, None]:
    """
    Return user object from the database, returns None if non-existent.
    """
    with database.get() as db:
        user = db["users"].find_one(username=username)
    return user if user else None