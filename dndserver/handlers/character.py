import random

from dndserver.database import db
from dndserver.enums import CharacterClass, Gender
from dndserver.models import Character
from dndserver.objects import items
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Account import (SC2S_ACCOUNT_CHARACTER_CREATE_REQ, SC2S_ACCOUNT_CHARACTER_DELETE_REQ,
                                      SC2S_ACCOUNT_CHARACTER_LIST_REQ, SLOGIN_CHARACTER_INFO,
                                      SS2C_ACCOUNT_CHARACTER_CREATE_RES, SS2C_ACCOUNT_CHARACTER_DELETE_RES,
                                      SS2C_ACCOUNT_CHARACTER_LIST_RES)
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_INFO
from dndserver.protos.Defines import Define_Character
from dndserver.protos.Lobby import SS2C_LOBBY_CHARACTER_INFO_RES


def list_characters(ctx, msg):
    """Occurs when the user loads in to the character selection screen."""
    req = SC2S_ACCOUNT_CHARACTER_LIST_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(user_id=ctx.sessions[ctx.transport]["user"].id).all()
    res = SS2C_ACCOUNT_CHARACTER_LIST_RES(totalCharacterCount=len(query), pageIndex=req.pageIndex)

    start = (res.pageIndex - 1) * 7
    end = start + 7

    for result in query[start:end]:
        res.characterList.append(SLOGIN_CHARACTER_INFO(
            characterId=str(result.id),
            nickName=SACCOUNT_NICKNAME(
                originalNickName=result.nickname,
                streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
            ),
            level=result.level,
            characterClass=CharacterClass(result.character_class).value,
            gender=Gender(result.gender).value,
            equipItemList=[
                items.generate_torch(), items.generate_roundshield(), items.generate_lantern(),
                items.generate_sword(), items.generate_pants(), items.generate_tunic(),
                items.generate_bandage(), items.generate_helm()
            ],
            createAt=result.created_at.int_timestamp,
            # lastloginDate=result.last_logged_at  # TODO: Need to implement access logs.
        ))

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

    character = Character(
        user_id=ctx.sessions[ctx.transport]["user"].id,
        nickname=req.nickName,
        gender=Gender(req.gender),
        character_class=CharacterClass(req.characterClass)
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
    if query.user_id != ctx.sessions[ctx.transport]["user"].id:
        res.result = pc.FAIL_GENERAL
        return res

    query.delete()
    return res


def character_info(ctx, msg):
    """Occurs when the user loads into the lobby/tavern."""
    query = db.query(Character).filter_by(user_id=ctx.sessions[ctx.transport]["user"].id).first()
    res = SS2C_LOBBY_CHARACTER_INFO_RES(
        result=pc.SUCCESS,
        characterDataBase=SCHARACTER_INFO(
            accountId="1",
            nickName=SACCOUNT_NICKNAME(
                originalNickName=query.nickname,
                streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
            ),
            characterClass=CharacterClass(query.character_class).value,
            characterId=str(query.id),
            gender=Gender(query.gender).value,
            level=query.level,
            CharacterItemList=[
                items.generate_helm(), items.generate_torch(), items.generate_lantern(),
                items.generate_sword(), items.generate_pants(), items.generate_tunic(),
                items.generate_bandage()
            ]
        )
    )
    return res
