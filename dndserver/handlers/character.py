from loguru import logger

from dndserver import database
from dndserver.objects import items
from dndserver.protos import Account_pb2 as acc
from dndserver.protos import _Character_pb2 as char


def list_characters(ctx, data: bytes):
    req = acc.SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(data[8:])
    # logger.debug(f"Received SC2S_ACCOUNT_CHARACTER_LIST_REQ:\n {req}")

    res = acc.SS2C_ACCOUNT_CHARACTER_LIST_RES()
    res.totalCharacterCount = 1  # TODO: Query the db and return all characters from the UID.
    res.pageIndex = 1            # TODO: Each page holds up to 7 characters, needs to be implemented

    nickname = char.SACCOUNT_NICKNAME()
    nickname.originalNickName = "Kroftydfg"  # str
    nickname.streamingModeNickName = "Fighter#1660779"  # str: Fighter#1660779

    character = acc.SLOGIN_CHARACTER_INFO()
    character.nickName.CopyFrom(nickname)
    character.characterId = "2784402"  # str
    character.characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"  # str
    character.createAt = 1681858691000  # int(time.time())  # int: unix timestamp
    character.gender = 1  # int: 1 = male, 2 = female
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

    # header = struct.pack(
    #     "<B3xI", len(res.SerializeToString()),
    #     pc.PacketCommand.Value("S2C_ACCOUNT_CHARACTER_LIST_RES")
    # )
    header = b"\xa7\x05\x00\x00\x12\x00\x00\x00"
    # logger.debug(f"Sent SS2C_ACCOUNT_CHARACTER_LIST_RES:\n {res}")
    logger.debug(f"Sent SS2C_ACCOUNT_CHARACTER_LIST_RES SERIAL+HEX:\n {(header + res.SerializeToString()).hex()}")
    return header + res.SerializeToString()


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
