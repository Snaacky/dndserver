import random
import time

from dndserver import database
from dndserver.objects import items
from dndserver.protos import Account_pb2 as acc
from dndserver.protos import _Character_pb2 as char
from dndserver.protos import _PacketCommand_pb2 as pc
from dndserver.protos import Lobby_pb2 as lb


def list_characters(ctx, data: bytes):
    req = acc.SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(data[8:])
    req.pageIndex = 1
    print(req)
    res = acc.SS2C_ACCOUNT_CHARACTER_LIST_RES()
    res.pageIndex = 1

    db = database.get()
    results = list(db["characters"].find(owner_id=ctx.sessions[ctx.transport]["accountId"]))

    start_index = (req.pageIndex - 1) * 7
    end_index = start_index + 7

    for result in results[start_index:end_index]:
        nickname = char.SACCOUNT_NICKNAME()
        nickname.originalNickName = result["nickname"]
        nickname.streamingModeNickName = f"Fighter#{random.randrange(1000000, 1700000)}"

        character = acc.SLOGIN_CHARACTER_INFO()
        character.nickName.CopyFrom(nickname)
        character.characterId = str(result["id"])
        character.characterClass = result["character_class"]
        character.createAt = result["created_at"]  # 1681858691000  # int(time.time())  # int: unix timestamp
        character.gender = result["gender"]  # int: 1 = male, 2 = female
        character.level = result["level"]   # int
        character.lastloginDate = result["last_logged_at"]  # int(time.time())  # int: unix timestamp

        character.equipItemList.append(items.generate_torch())
        character.equipItemList.append(items.generate_roundshield())
        character.equipItemList.append(items.generate_lantern())
        character.equipItemList.append(items.generate_sword())
        character.equipItemList.append(items.generate_pants())
        character.equipItemList.append(items.generate_tunic())
        character.equipItemList.append(items.generate_bandage())
        character.equipItemList.append(items.generate_helm())
        res.characterList.append(character)

    res.totalCharacterCount = len(results)

    return res


def create_character(ctx, data: bytes):
    req = acc.SC2S_ACCOUNT_CHARACTER_CREATE_REQ()
    req.ParseFromString(data[8:])

    res = acc.SS2C_ACCOUNT_CHARACTER_CREATE_RES()

    if len(req.nickName) < 2:
        res.result = pc.PacketResult.Value("FAIL_CHARACTER_NICKNAME_LENGTH_SHORTAGE")
        return res

    if len(req.nickName) > 20:
        res.result = pc.PacketResult.Value("FAIL_CHARACTER_NICKNAME_LENGTH_OVER")
        return res

    db = database.get()

    dupe = db["characters"].find_one(nickname=req.nickName)
    if dupe:
        res.result = pc.PacketResult.Value("FAIL_DUPLICATE_NICKNAME")
        return res

    db["characters"].insert(dict(
        owner_id=ctx.sessions[ctx.transport]["accountId"],
        nickname=req.nickName,
        gender=req.gender,
        character_class=req.characterClass,
        created_at=int(time.time()),
        level=1,
        last_logged_at=int(time.time())
    ))
    db.commit()
    db.close()

    res.result = 1
    return res


def delete_character(ctx, data: bytes):
    req = acc.SC2S_ACCOUNT_CHARACTER_DELETE_REQ()
    req.ParseFromString(data[8:])

    res = acc.SS2C_ACCOUNT_CHARACTER_DELETE_RES()

    db = database.get()
    char = db["characters"].find_one(id=req.characterId)

    # Prevents characters from maliciously deleting others characters.
    if char["owner_id"] != ctx.sessions[ctx.transport]["accountId"]:
        res.result = pc.PacketResult.Value("FAIL_GENERAL")
        return res

    db["characters"].delete(id=req.characterId)
    db.commit()
    db.close()

    res.result = pc.PacketResult.Value("SUCCESS")
    return res

def character_info(ctx, data: bytes):
    res = lb.SS2C_LOBBY_CHARACTER_INFO_RES()
    res.result = 1

    db = database.get()
    result = db["characters"].find_one(owner_id=ctx.sessions[ctx.transport]["accountId"])

    nickname = char.SACCOUNT_NICKNAME()
    nickname.originalNickName = result["nickname"]
    nickname.streamingModeNickName = f"Fighter#{random.randrange(1000000, 1700000)}"

    char_info = char.SCHARACTER_INFO()
    char_info.accountId = "1"
    char_info.nickName.CopyFrom(nickname)
    char_info.characterClass = result["character_class"]
    char_info.characterId = str(result["id"])
    char_info.gender = result["gender"]
    char_info.level = result["level"]
    char_info.CharacterItemList.append(items.generate_helm())
    char_info.CharacterItemList.append(items.generate_torch())
    #char_info.CharacterItemList.append(items.generate_roundshield())
    char_info.CharacterItemList.append(items.generate_lantern())
    char_info.CharacterItemList.append(items.generate_sword())
    char_info.CharacterItemList.append(items.generate_pants())
    char_info.CharacterItemList.append(items.generate_tunic())
    char_info.CharacterItemList.append(items.generate_bandage())
    
    res.characterDataBase.CopyFrom(char_info)
    return res