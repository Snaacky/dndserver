import random

from dndserver import database
from dndserver.objects import items
from dndserver.protos import Account_pb2 as acc
from dndserver.protos import _Character_pb2 as char


def list_characters(ctx, data: bytes):
    req = acc.SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(data[8:])

    res = acc.SS2C_ACCOUNT_CHARACTER_LIST_RES()
    res.totalCharacterCount = 1  # TODO: Query the db and return all characters from the UID.
    res.pageIndex = 1            # TODO: Each page holds up to 7 characters, needs to be implemented

    nickname = char.SACCOUNT_NICKNAME()
    nickname.originalNickName = "Snaacky"
    nickname.streamingModeNickName = f"Fighter#{random.range(1000000, 1700000)}"

    character = acc.SLOGIN_CHARACTER_INFO()
    character.nickName.CopyFrom(nickname)
    character.characterId = "1"
    character.characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Barbarian"
    character.createAt = 1681858691000  # int(time.time())  # int: unix timestamp
    character.gender = 2  # int: 1 = male, 2 = female
    character.level = 1   # int
    character.lastloginDate = 1681858691000  # int(time.time())  # int: unix timestamp

    character.equipItemList.append(items.generate_torch())
    character.equipItemList.append(items.generate_roundshield())
    character.equipItemList.append(items.generate_lantern())
    character.equipItemList.append(items.generate_sword())
    character.equipItemList.append(items.generate_pants())
    character.equipItemList.append(items.generate_tunic())
    character.equipItemList.append(items.generate_bandage())
    res.characterList.append(character)

    return res.SerializeToString()


def create_character(ctx, data: bytes):
    queue = []

    req = acc.SC2S_ACCOUNT_CHARACTER_CREATE_REQ()
    req.ParseFromString(data[8:])
    # logger.debug(req)

    # send character res first
    resp = acc.SS2C_ACCOUNT_CHARACTER_CREATE_RES()
    resp.result = 1
    queue.append(resp)

    db = database.get()
    db["characters"].insert(dict(
        owner_id=1,
        nickname=req.nickName,
        character_class=req.characterClass,
        gender=req.gender
    ))
    db.commit()
    db.close()

    # then send the character info second
    # char_info_resp = SS2C_LOBBY_CHARACTER_INFO_RES()
    # character_info = SCHARACTER_INFO()
    # character_info.accountId = "456456"
    # character_info.nickName = "dfgdfg"
    # characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"
    # characterId = "45345"
    # gender = 1
    # level = 1
    # servicegrpc = "???"
    # characteritemlist = SomeCharacterItemList()
    # characterstorageitemlist = SomeCharacterStorageItemList()
    #
    # resp.characterDatabase.CopyFrom(character_info)
    return resp.SerializeToString()
