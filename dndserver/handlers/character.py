import random

from dndserver.database import db
from dndserver.enums import CharacterClass, Gender
from dndserver.models import Character, Item, ItemAttribute
from dndserver import objects
from dndserver.protos import PacketCommand as pc
from dndserver.protos import Item as pItem
from dndserver.protos.Account import (
    SC2S_ACCOUNT_CHARACTER_CREATE_REQ,
    SC2S_ACCOUNT_CHARACTER_DELETE_REQ,
    SC2S_ACCOUNT_CHARACTER_LIST_REQ,
    SLOGIN_CHARACTER_INFO,
    SS2C_ACCOUNT_CHARACTER_CREATE_RES,
    SS2C_ACCOUNT_CHARACTER_DELETE_RES,
    SS2C_ACCOUNT_CHARACTER_LIST_RES,
)
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_INFO
from dndserver.protos.CharacterClass import (
    SCLASS_EQUIP_INFO,
    SS2C_CLASS_EQUIP_INFO_RES,
    SS2C_CLASS_PERK_LIST_RES,
    SC2S_CLASS_ITEM_MOVE_REQ,
    SS2C_CLASS_ITEM_MOVE_RES,
    SS2C_CLASS_SKILL_LIST_RES,
    SS2C_CLASS_LEVEL_INFO_RES,
)
from dndserver.protos.Customize import SS2C_CUSTOMIZE_CHARACTER_INFO_RES
from dndserver.protos.Item import SCUSTOMIZE_CHARACTER
from dndserver.protos.Defines import Define_Character, Define_Class, Define_Item
from dndserver.protos.Lobby import SS2C_LOBBY_CHARACTER_INFO_RES
from dndserver.sessions import sessions
from dndserver.data import perks as pk
from dndserver.data import skills as sk


def item_to_proto_item(item, attributes):
    """Helper function to create a proto item from a database item and attributes"""
    ret = pItem.SItem()

    ret.itemUniqueId = item.id
    ret.itemId = item.item_id
    ret.itemCount = item.quantity
    ret.inventoryId = item.inventory_id
    ret.slotId = item.slot_id
    ret.itemAmmoCount = item.id
    ret.itemContentsCount = item.id

    for attribute in attributes:
        property = pItem.SItemProperty(propertyTypeId=attribute.property, propertyValue=attribute.value)

        if attribute.primary:
            ret.primaryPropertyArray.append(property)
        else:
            ret.secondaryPropertyArray.append(property)

    return ret


def get_all_items(character_id):
    """Helper function to get all items for a character id"""
    query = db.query(Item).filter_by(character_id=character_id)
    ret = list()

    for item in query:
        # add the attributes of the item
        attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()

        # add the attributes and the item
        ret.append((item, attributes))

    return ret


def list_characters(ctx, msg):
    """Occurs when the user loads in to the character selection screen."""
    req = SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(user_id=sessions[ctx.transport].account.id).all()
    res = SS2C_ACCOUNT_CHARACTER_LIST_RES(totalCharacterCount=len(query), pageIndex=req.pageIndex)

    start = (res.pageIndex - 1) * 7
    end = start + 7

    for result in query[start:end]:
        info = SLOGIN_CHARACTER_INFO(
            characterId=str(result.id),
            nickName=SACCOUNT_NICKNAME(
                originalNickName=result.nickname, streamingModeNickName=result.streaming_nickname
            ),
            level=result.level,
            characterClass=CharacterClass(result.character_class).value,
            gender=Gender(result.gender).value,
            createAt=result.created_at.int_timestamp,
            # lastloginDate=result.last_logged_at  # TODO: Need to implement access logs.
        )

        for item, attributes in get_all_items(result.id):
            if item.inventory_id != Define_Item.InventoryId.EQUIPMENT:
                continue

            info.equipItemList.append(item_to_proto_item(item, attributes))

        res.characterList.append(info)

    return res


def create_character(ctx, msg):
    """Occurs when the user attempts to create a new character."""
    req = SC2S_ACCOUNT_CHARACTER_CREATE_REQ()
    req.ParseFromString(msg)

    res = SS2C_ACCOUNT_CHARACTER_CREATE_RES(result=pc.SUCCESS)

    if len(req.nickName) < Define_Character.MIN:
        res.result = pc.FAIL_CHARACTER_NICKNAME_LENGTH_SHORTAGE
        return res

    if len(req.nickName) > Define_Character.MAX:
        res.result = pc.FAIL_CHARACTER_NICKNAME_LENGTH_OVER
        return res

    if db.query(Character).filter_by(nickname=req.nickName).first():
        res.result = pc.FAIL_DUPLICATE_NICKNAME
        return res

    char = Character(
        user_id=sessions[ctx.transport].account.id,
        nickname=req.nickName,
        streaming_nickname=f"Fighter#{random.randrange(1000000, 1700000)}",
        gender=Gender(req.gender),
        character_class=CharacterClass(req.characterClass),
    )

    # select the default perks and skills
    char.perk0 = pk.perks[CharacterClass(req.characterClass)][0]
    char.skill0, char.skill1 = sk.skills[CharacterClass(req.characterClass)][0:2]
    char.save()

    # TODO: make this dependend on the character class
    starter_items = [
        objects.items.generate_helm(),
        objects.items.generate_torch(),
        objects.items.generate_lantern(),
        objects.items.generate_sword(),
        objects.items.generate_pants(),
        objects.items.generate_tunic(),
        objects.items.generate_bandage(),
    ]

    # give the character a starter set
    for item in starter_items:
        # we ignore the unique id here of the item. The database knows best what the id should be
        it = Item()
        it.character_id = char.id
        it.item_id = item.itemId
        it.quantity = item.itemCount
        it.inventory_id = item.inventoryId
        it.slot_id = item.slotId

        it.save()

        # add the attributes to the items
        for attribute in item.primaryPropertyArray:
            attr = ItemAttribute()
            attr.item_id = it.id
            attr.primary = True
            attr.property = attribute.propertyTypeId
            attr.value = attribute.propertyValue

            attr.save()

        for attribute in item.secondaryPropertyArray:
            attr = ItemAttribute()
            attr.item_id = it.id
            attr.primary = False
            attr.property = attribute.propertyTypeId
            attr.value = attribute.propertyValue

            attr.save()

    return res


def delete_character(ctx, msg):
    """Occurs when the user attempts to delete a character."""
    req = SC2S_ACCOUNT_CHARACTER_DELETE_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(id=req.characterId).first()
    res = SS2C_ACCOUNT_CHARACTER_DELETE_RES(result=pc.SUCCESS)

    # Prevents characters from maliciously deleting others characters.
    if query.user_id != sessions[ctx.transport].account.id:
        res.result = pc.FAIL_GENERAL
        return res

    # also delete all the items this character has
    items = db.query(Item).filter_by(character_id=req.characterId)
    for item in items:
        # delete all the attributes of the items we are deleting
        attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()

        for attribute in attributes:
            attribute.delete()

        item.delete()

    # delete the character after we have removed all the other items
    query.delete()
    return res


def customise_character_info(ctx, msg):
    custom = SCUSTOMIZE_CHARACTER(customizeCharacterId="1", isEquip=1, isNew=1)
    res = SS2C_CUSTOMIZE_CHARACTER_INFO_RES()
    res.loopFlag = 0
    res.customizeCharacters.append(custom)
    return res


def character_info(ctx, msg):
    """Occurs when the user loads into the lobby/tavern."""
    character = sessions[ctx.transport].character

    char_info = SCHARACTER_INFO(
        accountId=str(sessions[ctx.transport].account.id),
        nickName=SACCOUNT_NICKNAME(
            originalNickName=character.nickname, streamingModeNickName=character.streaming_nickname
        ),
        characterClass=CharacterClass(character.character_class).value,
        characterId=str(character.id),
        gender=Gender(character.gender).value,
        level=character.level,
    )

    # get all the items and attributes of the character
    for item, attributes in get_all_items(character.id):
        char_info.CharacterItemList.append(item_to_proto_item(item, attributes))

    res = SS2C_LOBBY_CHARACTER_INFO_RES(result=pc.SUCCESS, characterDataBase=char_info)

    return res


def get_experience(ctx, msg):
    """Occurs when the user loads into the lobby."""
    character = sessions[ctx.transport].character
    res = SS2C_CLASS_LEVEL_INFO_RES()

    res.level = character.level
    res.exp = character.experience
    res.expBegin = 0

    # 1 - 4 = 40 exp, 5 - 9 = 60 exp, 10 - 14 = 80 exp, 15 - 19 = 100
    res.expLimit = 40 + (int(character.level / 5) * 20)

    return res


def list_perks(ctx, msg):
    """Occurs when user selects the class menu."""
    character = sessions[ctx.transport].character
    selected_perks = [character.perk0, character.perk1, character.perk2, character.perk3]

    res = SS2C_CLASS_PERK_LIST_RES()
    perks = pk.perks[character.character_class]
    index = 0

    # Generate the response. Do not send the perks we have selected already
    for perk in perks:
        if perk not in selected_perks:
            res.perks.append(pItem.SPerk(index=index, perkId=perk))
            index += 1

    return res


def list_skills(ctx, msg):
    """Occurs when user selects the class menu."""
    character = sessions[ctx.transport].character
    selected_skills = [character.skill0, character.skill1]

    res = SS2C_CLASS_SKILL_LIST_RES()
    skills = sk.skills[character.character_class]
    index = 0

    # Generate the response. Do not send the skills we have selected already
    for skill in skills:
        if skill not in selected_skills:
            res.skills.append(pItem.SSkill(index=index, skillId=skill))
            index += 1

    return res


def get_perks_and_skills(ctx, msg):
    """Occurs when the user loads in the game or loads into the class menu."""
    character = sessions[ctx.transport].character
    res = SS2C_CLASS_EQUIP_INFO_RES()

    # level requirements for the 4 perks
    perks = [character.perk0, character.perk1, character.perk2, character.perk3]

    for index, perk in enumerate(perks):
        res.equips.append(
            SCLASS_EQUIP_INFO(
                index=index + 1,
                isAvailableSlot=True,
                requiredLevel=pk.level_requirements[index],
                type=Define_Class.Type.PERK,
                equipId=perk,
            )
        )

    skills = [character.skill0, character.skill1]
    for index, skill in enumerate(skills):
        res.equips.append(
            SCLASS_EQUIP_INFO(
                index=5 + index,
                isAvailableSlot=True,
                requiredLevel=1,
                type=Define_Class.Type.SKILL,
                equipId=skill,
            )
        )

    return res


def move_perks_and_skills(ctx, msg):
    """Occurs when the user tries to move either a perk or a skill."""
    req = SC2S_CLASS_ITEM_MOVE_REQ()
    req.ParseFromString(msg)

    char = sessions[ctx.transport].character
    items = [req.oldMove, req.newMove]

    # first check if we have the correct level to do this action
    for it in items:
        # check if the level requirements are met
        if it.index and char.level < pk.level_requirements[it.index - 1]:
            return SS2C_CLASS_ITEM_MOVE_RES(result=pc.SUCCESS)

    # process all the move requests
    for it in items:
        if it.type == Define_Class.Type.NONE_TYPE or it.move == Define_Class.Move.NONE_MOVE:
            # skip all items that are not moved and are of type none
            continue

        if it.type == Define_Class.Type.SPELL:
            # this should never happen but catch it anyway
            continue

        # get all the perks and the perks we have selected
        perks_skills = [char.perk0, char.perk1, char.perk2, char.perk3, char.skill0, char.skill1]

        # update the perks
        if it.move == Define_Class.Move.EQUIP:
            perks_skills[it.index - 1] = it.moveId
        elif it.move == Define_Class.Move.UN_EQUIP:
            perks_skills[it.index - 1] = ""

        # store the perks and skills back
        char.perk0, char.perk1, char.perk2, char.perk3, char.skill0, char.skill1 = perks_skills

    return SS2C_CLASS_ITEM_MOVE_RES(result=pc.SUCCESS, oldMove=req.oldMove, newMove=req.newMove)
