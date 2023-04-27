import random

from dndserver.database import db
from dndserver.enums import CharacterClass, Gender
from dndserver.models import Character
from dndserver.objects import items
from dndserver.protos import PacketCommand as pc
from dndserver.protos import Item as item
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
from dndserver.protos.Defines import Define_Character, Define_Class
from dndserver.protos.Lobby import SS2C_LOBBY_CHARACTER_INFO_RES
from dndserver.protos.Inventory import SC2S_INVENTORY_SINGLE_UPDATE_REQ, SS2C_INVENTORY_SINGLE_UPDATE_RES
from dndserver.sessions import sessions
from dndserver.data import perks as pk
from dndserver.data import skills as sk


def list_characters(ctx, msg):
    """Occurs when the user loads in to the character selection screen."""
    req = SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(user_id=sessions[ctx.transport].account.id).all()
    res = SS2C_ACCOUNT_CHARACTER_LIST_RES(totalCharacterCount=len(query), pageIndex=req.pageIndex)

    start = (res.pageIndex - 1) * 7
    end = start + 7

    for result in query[start:end]:
        res.characterList.append(
            SLOGIN_CHARACTER_INFO(
                characterId=str(result.id),
                nickName=SACCOUNT_NICKNAME(
                    originalNickName=result.nickname,
                    streamingModeNickName=result.streaming_nickname
                ),
                level=result.level,
                characterClass=CharacterClass(result.character_class).value,
                gender=Gender(result.gender).value,
                equipItemList=[
                    items.generate_torch(),
                    items.generate_roundshield(),
                    items.generate_lantern(),
                    items.generate_sword(),
                    items.generate_pants(),
                    items.generate_tunic(),
                    items.generate_bandage(),
                    items.generate_helm()
                ],
                createAt=result.created_at.int_timestamp,
                # lastloginDate=result.last_logged_at  # TODO: Need to implement access logs.
            )
        )

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
    char.perk0, char.perk1, char.perk2, char.perk3 = pk.perks[CharacterClass(req.characterClass)][0:4]
    char.skill0, char.skill1 = sk.skills[CharacterClass(req.characterClass)][0:2]
    char.save()

    return res


def delete_character(ctx, msg):
    """Occurs when the user attempts to delete a character."""
    req = SC2S_ACCOUNT_CHARACTER_DELETE_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(id=req.characterId).first()
    res = SS2C_ACCOUNT_CHARACTER_DELETE_RES(result=pc.SUCCESS)

    # Prevents characters from maliciously deleting others characters.
    if query.user_id != sessions[ctx.transport].user.id:
        res.result = pc.FAIL_GENERAL
        return res

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

    res = SS2C_LOBBY_CHARACTER_INFO_RES(
        result=pc.SUCCESS,
        characterDataBase=SCHARACTER_INFO(
            accountId="1",
            nickName=SACCOUNT_NICKNAME(
                originalNickName=character.nickname,
                streamingModeNickName=character.streaming_nickname
            ),
            characterClass=CharacterClass(character.character_class).value,
            characterId=str(character.id),
            gender=Gender(character.gender).value,
            level=character.level,
            CharacterItemList=[
                items.generate_helm(),
                items.generate_torch(),
                items.generate_lantern(),
                items.generate_sword(),
                items.generate_pants(),
                items.generate_tunic(),
                items.generate_bandage(),
            ],
        ),
    )

    return res

    return res


def get_experience(ctx, msg):
    """Occurs when the user loads into the lobby."""
    query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()
    res = SS2C_CLASS_LEVEL_INFO_RES()

    res.level = query.level
    res.exp = query.experience
    res.expBegin = 0

    # 1 - 4 = 40 exp, 5 - 9 = 60 exp, 10 - 14 = 80 exp, 15 - 19 = 100
    res.expLimit = 40 + (int(query.level / 5) * 20)

    return res


def move_item(ctx, msg):
    req = SC2S_INVENTORY_SINGLE_UPDATE_REQ()
    req.ParseFromString(msg)
    res = SS2C_INVENTORY_SINGLE_UPDATE_RES(result=pc.SUCCESS, oldItem=req.oldItem, newItem=req.newItem)
    return res


def list_perks(ctx, msg):
    """Occurs when user selects the class menu."""
    query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()
    selected_perks = [query.perk0, query.perk1, query.perk2, query.perk3]

    res = SS2C_CLASS_PERK_LIST_RES()
    perks = pk.perks[query.character_class]
    index = 0

    # Generate the response. Do not send the perks we have selected already
    for perk in perks:
        if perk not in selected_perks:
            res.perks.append(item.SPerk(index=index, perkId=perk))
            index += 1

    return res


def list_skills(ctx, msg):
    """Occurs when user selects the class menu."""
    query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()
    selected_skills = [query.skill0, query.skill1]

    res = SS2C_CLASS_SKILL_LIST_RES()
    skills = sk.skills[query.character_class]
    index = 0

    # Generate the response. Do not send the skills we have selected already
    for skill in skills:
        if skill not in selected_skills:
            res.skills.append(item.SSkill(index=index, skillId=skill))
            index += 1

    return res


def get_perks_and_skills(ctx, msg):
    """Occurs when the user loads in the game or loads into the class menu."""
    query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()
    res = SS2C_CLASS_EQUIP_INFO_RES()

    # level requirements for the 4 perks
    level = [1, 5, 10, 15]
    perks = [query.perk0, query.perk1, query.perk2, query.perk3]

    for index, perk in enumerate(perks):
        res.equips.append(
            SCLASS_EQUIP_INFO(
                index=index + 1,
                isAvailableSlot=True,
                requiredLevel=level[index],
                type=Define_Class.Type.PERK,
                equipId=perk,
            )
        )

    skills = [query.skill0, query.skill1]
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

    query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()
    items = [req.oldMove, req.newMove]

    # process all the move requests
    for it in items:
        if it.type == Define_Class.Type.NONE_TYPE or it.move == Define_Class.Move.NONE_MOVE:
            # skip all items that are not moved and are of type none
            continue

        if it.type == Define_Class.Type.SPELL:
            # this should never happen but catch it anyway
            continue

        # get all the perks and the perks we have selected
        perks_skills = [query.perk0, query.perk1, query.perk2, query.perk3, query.skill0, query.skill1]

        # update the perks
        if it.move == Define_Class.Move.EQUIP:
            perks_skills[it.index - 1] = it.moveId
        elif it.move == Define_Class.Move.UN_EQUIP:
            perks_skills[it.index - 1] = ""

        # store the perks and skills back
        query.perk0, query.perk1, query.perk2, query.perk3, query.skill0, query.skill1 = perks_skills

    return SS2C_CLASS_ITEM_MOVE_RES(result=pc.SUCCESS, oldMove=req.oldMove, newMove=req.newMove)
