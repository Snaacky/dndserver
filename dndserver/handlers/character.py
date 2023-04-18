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
    
    
    resp = SS2C_LOBBY_CHARACTER_INFO_RES()

    character_info = SCHARACTER_INFO()
    character_info.accountId = "456456"
    character_info.nickName = "dfgdfg"
    characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"
    characterId = "45345"
    gender = 1
    level = 1
    servicegrpc = "???"
    characteritemlist = SomeCharacterItemList()
    characterstorageitemlist = SomeCharacterStorageItemList()

    resp.characterDatabase.CopyFrom(character_info)


    return resp.SerializeToString()
