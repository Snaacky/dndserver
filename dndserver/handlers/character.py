import struct

from loguru import logger

from dndserver import database
from dndserver.protos import Account_pb2 as acc
from dndserver.protos import _Character_pb2 as char
from dndserver.protos import _Item_pb2 as item
from dndserver.protos import _PacketCommand_pb2 as pc


def list_characters(self, data: bytes):
    req = acc.SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(data[8:])
    logger.debug(f"Received SC2S_ACCOUNT_CHARACTER_LIST_REQ:\n {req}")

    nickname = char.SACCOUNT_NICKNAME()
    nickname.originalNickName = "Snaacky"  # str
    nickname.streamingModeNickName = "Snaacky"  # str
    nickname.karmaRating = 1  # int

    primary = item.SItemProperty()
    primary.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    primary.propertyValue = 1

    secondary = item.SItemProperty()
    secondary.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_PhysicalWeaponDamage"
    secondary.propertyValue = 1

    # torch = item.SItem()
    # torch.itemUniqueId = 1
    # torch.itemId = "DesignDataItem:Id_Item_Torch_0001"
    # torch.itemCount = 1
    # torch.inventoryId = 1
    # torch.slotId = 1
    # torch.itemAmmoCount = 1
    # torch.itemContentsCount = 1
    # torch.primaryPropertyArray.append(primary)
    # torch.secondaryPropertyArray.append(primary)

    character = acc.SLOGIN_CHARACTER_INFO()
    character.nickName.CopyFrom(nickname)
    character.characterId = "1"  # str
    character.characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"  # str
    character.createAt = 0  # int
    character.gender = 1    # int
    character.level = 1     # int
    character.lastloginDate = 1  # int
    # character.equipItemList.append(torch)
    # character.equipItemSkinList.append("")
    # character.equipCharacterSkinList.append("")
    # character.equipCharacterSkinList = []  # repeated string equipCharacterSkinList = 9;
    # character.equipItemSkinList = []       # repeated string equipItemSkinList = 10;

    res = acc.SS2C_ACCOUNT_CHARACTER_LIST_RES()
    res.totalCharacterCount = 1  # TODO: Query the db and return all characters from the UID.
    res.pageIndex = 0  # TODO: Each page holds up to 7 characters, needs to be implemented
    res.characterList.append(character)

    header = struct.pack(
        "<B3xI", len(res.SerializeToString()),
        pc.PacketCommand.Value("S2C_ACCOUNT_CHARACTER_LIST_RES")
    )
    logger.debug(f"Sent SS2C_ACCOUNT_CHARACTER_LIST_RES:\n {res}")
    logger.debug(f"Sent SS2C_ACCOUNT_CHARACTER_LIST_RES serialized:\n {res.SerializeToString()}")
    return header + res.SerializeToString()


def create_character(self, data: bytes):
    queue = []

    req = acc.SC2S_ACCOUNT_CHARACTER_CREATE_REQ()
    req.ParseFromString(data[8:])
    logger.debug(req)

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
