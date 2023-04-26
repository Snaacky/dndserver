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
    SC2S_CLASS_SPELL_LIST_REQ,
    SS2C_CLASS_SPELL_LIST_RES,
)
from dndserver.protos.Defines import Define_Character, Define_Class
from dndserver.protos.Lobby import SS2C_LOBBY_CHARACTER_INFO_RES
from dndserver.sessions import sessions
from dndserver import perksandskills


def list_characters(ctx, msg):
    """Occurs when the user loads in to the character selection screen."""
    req = SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(user_id=sessions[ctx.transport]["user"].id).all()
    res = SS2C_ACCOUNT_CHARACTER_LIST_RES(totalCharacterCount=len(query), pageIndex=req.pageIndex)

    start = (res.pageIndex - 1) * 7
    end = start + 7

    for result in query[start:end]:
        res.characterList.append(
            SLOGIN_CHARACTER_INFO(
                characterId=str(result.id),
                nickName=SACCOUNT_NICKNAME(
                    originalNickName=result.nickname,
                    streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}",
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
                    items.generate_helm(),
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

    character_class = CharacterClass(req.characterClass)
    character = Character(
        user_id=sessions[ctx.transport]["user"].id,
        nickname=req.nickName,
        gender=Gender(req.gender),
        character_class=character_class,
        perk0=perksandskills.perks[character_class][0],
        perk1=perksandskills.perks[character_class][1],
        perk2=perksandskills.perks[character_class][2],
        perk3=perksandskills.perks[character_class][3],
    )

    character.save()
    return res


def delete_character(ctx, msg):
    """Occurs when the user attempts to delete a character."""
    req = SC2S_ACCOUNT_CHARACTER_DELETE_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(id=req.characterId).first()
    res = SS2C_ACCOUNT_CHARACTER_DELETE_RES(result=pc.SUCCESS)

    # Prevents characters from maliciously deleting others characters.
    if query.user_id != sessions[ctx.transport]["user"].id:
        res.result = pc.FAIL_GENERAL
        return res

    query.delete()
    return res


def character_info(ctx, msg):
    """Occurs when the user loads into the lobby/tavern."""
    query = db.query(Character).filter_by(user_id=sessions[ctx.transport]["user"].id).first()
    res = SS2C_LOBBY_CHARACTER_INFO_RES(
        result=pc.SUCCESS,
        characterDataBase=SCHARACTER_INFO(
            accountId="1",
            nickName=SACCOUNT_NICKNAME(
                originalNickName=query.nickname, streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
            ),
            characterClass=CharacterClass(query.character_class).value,
            characterId=str(query.id),
            gender=Gender(query.gender).value,
            level=query.level,
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


def move_perks_and_skills(ctx, msg):
    req = SC2S_CLASS_ITEM_MOVE_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(user_id=sessions[ctx.transport]["user"].id).first()
    items = [req.oldMove, req.newMove]

    # process all the move requests
    for it in items:
        if it.type == Define_Class.Type.NONE_TYPE or it.move == Define_Class.Move.NONE_MOVE:
            # skip all items that are not moved and are of type none
            continue

        if it.type == Define_Class.Type.PERK:
            # get all the perks we have
            perks = [query.perk0, query.perk1, query.perk2, query.perk3]

            # update the perks
            if it.move == Define_Class.Move.EQUIP:
                perks[it.index - 1] = it.moveId
            elif it.move == Define_Class.Move.UN_EQUIP:
                perks[it.index - 1] = ""

            # store the perks back
            query.perk0, query.perk1, query.perk2, query.perk3 = perks

    res = SS2C_CLASS_ITEM_MOVE_RES(result=pc.SUCCESS, oldMove=req.oldMove, newMove=req.newMove)
    return res


def list_perks(ctx, msg):
    query = db.query(Character).filter_by(user_id=sessions[ctx.transport]["user"].id).first()
    selected_perks = [query.perk0, query.perk1, query.perk2, query.perk3]

    res = SS2C_CLASS_PERK_LIST_RES()
    perks = perksandskills.perks[query.character_class]
    index = 0

    # Generate the response. Do not send the perks we have selected already
    for perk in perks:
        if perk not in selected_perks:
            res.perks.append(item.SPerk(index=index, perkId=perk))

            index += 1

    return res


def list_skills(ctx, msg):
    # TODO: add support for skills
    return SS2C_CLASS_SKILL_LIST_RES()


def list_spells(ctx, msg):
    # TODO: add support for spells
    req = SC2S_CLASS_SPELL_LIST_REQ()
    req.ParseFromString(msg)

    return SS2C_CLASS_SPELL_LIST_RES()


def get_perks_and_skills(ctx, msg):
    query = db.query(Character).filter_by(user_id=sessions[ctx.transport]["user"].id).first()
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

    # check if we should send the spells
    if query.character_class != CharacterClass.WIZARD and query.character_class != CharacterClass.CLERIC:
        return res

    # get the spells from the json
    spells = [
        query.spell0,
        query.spell1,
        query.spell2,
        query.spell3,
        query.spell4,
        query.spell5,
        query.spell6,
        query.spell7,
        query.spell8,
        query.spell9,
    ]
    for index, spell in enumerate(spells):
        res.equips.append(
            SCLASS_EQUIP_INFO(
                index=7 + index, isAvailableSlot=True, requiredLevel=1, type=Define_Class.Type.SPELL, equipId=spell
            )
        )

    return res
