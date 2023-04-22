import random
import string
from typing import Union, Dict

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from loguru import logger

from dndserver import database
from dndserver.protos import Account_pb2 as acc

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Create a base class for SQLAlchemy models
Base = declarative_base()

# Define a User model for the database
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    build_version = Column(String)
    is_banned = Column(Integer)
    secret_token = Column(String)
    ip_address = Column(String)

    hwids = relationship("HwId", back_populates="user")

# Define a HwId model for the database
class HwId(Base):
    __tablename__ = 'hwids'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hwid = Column(String)

    user = relationship("User", back_populates="hwids")

# Check if the given hwid is associated with a banned user
def is_banned_hwid(hwid):
    # Create a database connection
    engine = create_engine('sqlite:///dndserver.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query the database to find a banned user with the given hwid
    banned_user = session.query(User, HwId).join(HwId, User.id == HwId.user_id)\
                   .filter(HwId.hwid == hwid, User.is_banned.isnot(None)).first()

    session.close()

    if banned_user:
        return True
    return False

# Get a user by their username
def get_user(username: str) -> Union[Dict, bool]:
    """
    Return user object from the database if not banned, returns False if non-existent,
    and returns None if the user is banned.
    """
    with database.get() as db:
        user = db["users"].find_one(username=username)
        if user and user["is_banned"]:
            return None
    return user if user else False

# Process login requests and respond accordingly
def process_login(self, data: bytes):
    # Deserialize the incoming data
    req = acc.SC2S_ACCOUNT_LOGIN_REQ()
    req.ParseFromString(data[8:])

    # Attempt to get the user requested and register an account if necessary
    user = get_user(req.loginId)
    res = acc.SS2C_ACCOUNT_LOGIN_RES()

    # Check if the user is banned
    if user and user["is_banned"]:
        # Return FAIL_USER_BANNED if the user is banned
        res.Result = 3  # Use error code 3 (invalid password) instead of 8
        account_info = acc.SLOGIN_ACCOUNT_INFO()
        account_info.AccountID = ""  # Set an empty AccountID in this case
        res.AccountInfo.CopyFrom(account_info)
    elif not user:
        # Register a new user if not found
        register_user(
            username=req.loginId, password=req.password, ip_address=self.transport.client[0], hwid=req.hwIds[0],
            build_version=req.buildVersion
        )

        user = get_user(req.loginId)
        if user is None:
            # If user is banned after registration (which should not happen)
            res.Result = 8  # Define a new error code for this case
            account_info = acc.SLOGIN_ACCOUNT_INFO()
            account_info.AccountID = ""  # Set an empty AccountID in this case
            res.AccountInfo.CopyFrom(account_info)

            return res.SerializeToString()  
        else:
            # Check if the HWID exists for the user, add it if not
            hwid = get_hwid(user["id"], req.hwIds[0])
            if not hwid:
                add_hwid(user["id"], req.hwIds[0])

            res = acc.SS2C_ACCOUNT_LOGIN_RES()

            # Return FAIL_SHORT_ID_OR_PASSWORD on too short username/password
            if len(req.loginId) <= 2 or len(req.password) <= 2:
                res.Result = 5
                account_info = acc.SLOGIN_ACCOUNT_INFO()
                account_info.AccountID = str(user["id"])
                res.AccountInfo.CopyFrom(account_info)
                return res.SerializeToString()

            # Return FAIL_OVERFLOW_ID_OR_PASSWORD on too long username
            if len(req.loginId) > 20:
                res.Result = 6
                account_info = acc.SLOGIN_ACCOUNT_INFO()
                account_info.AccountID = str(user["id"])
                res.AccountInfo.CopyFrom(account_info)
                return res.SerializeToString()

            # Check if the password matches
            if not PasswordHasher().verify(user["password"], req.password):
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

    # If login was not successful, return a serialized error response
    error_response = pc.SS2C_ACCOUNT_LOGIN_RES()
    error_response.result = pc.LoginResult.LOGIN_FAILED  # or any appropriate error code
    return error_response.SerializeToString()

# Register a new user and store their initial HWID
def register_user(username: str, password: str, hwid: str, build_version: str, ip_address: str) -> Dict:
    """
    Register a new user and store their initial HWID.
    Returns the newly created user object.
    """
    with database.get() as db:
        # Check if a user with the same username already exists
        existing_user = db["users"].find_one(username=username)
        if existing_user:
            return existing_user
        
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
def get_user(username: str) -> Union[Dict, bool]:
    """
    Return user object from the database, returns False if non-existent.
    """
    with database.get() as db:
        user = db["users"].find_one(username=username)
    return user if user else False