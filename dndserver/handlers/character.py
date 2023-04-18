import random
import string

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from loguru import logger

from dndserver import database
from dndserver.protos import Account_pb2 as account


def process_character(self, data: bytes):
    req = account.SC2S_ACCOUNT_CHARACTER_CREATE_REQ()
    req.ParseFromString(data[8:])
    logger.debug(req)
    
    resp = account.SS2C_ACCOUNT_CHARACTER_CREATE_RES()
    
    resp.result = 1


    return resp.SerializeToString()
