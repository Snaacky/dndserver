import random

from dndserver.database import db
from dndserver.enums import CharacterClass, Gender
from dndserver.models import Character
from dndserver.objects import items
from dndserver.protos import Account as acc, Character as char, Defines as df, Lobby as lb, PacketCommand as pc


def list_characters(ctx, req):
    """Occurs when the user loads in to the character selection screen."""
    query = db.query(Character).filter_by(user_id=ctx.sessions[ctx.transport]["user"].id).all()

    res = acc.SS2C_ACCOUNT_CHARACTER_LIST_RES()
    res.totalCharacterCount = len(query)
    res.pageIndex = req.pageIndex = 1

    start = (req.pageIndex - 1) * 7
    end = start + 7

    for result in query[start:end]:
        info = acc.SLOGIN_CHARACTER_INFO(
            characterId=str(result.id),
            nickName=char.SACCOUNT_NICKNAME(
                originalNickName=result.nickname,
                streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
            ),
            characterClass=CharacterClass(result.character_class),
            level=result.level,
            gender=Gender(result.gender),
            equipItemList=[
                items.generate_torch(), items.generate_roundshield, items.generate_lantern(),
                items.generate_sword(), items.generate_pants(), items.generate_tunic(),
                items.generate_bandage(), items.generate_helm()
            ],
            createAt=result.created_at,
            # lastloginDate=result.last_logged_at
        )

        res.characterList.append(info)

    return res


def create_character(ctx, req):
    """Occurs when the user attempts to create a new character."""
    res = acc.SS2C_ACCOUNT_CHARACTER_CREATE_RES()
    res.result = 1

    pr = pc.PacketResult

    if len(req.nickName) < df.Define_Character.MIN:
        res.result = pr.FAIL_CHARACTER_NICKNAME_LENGTH_SHORTAGE.Value()
        return res

    if len(req.nickName) > df.Define_Character.MAX:
        res.result = pr.FAIL_CHARACTER_NICKNAME_LENGTH_OVER.Value()
        return res

    if db.query(Character).filter_by(nickname=req.nickName).first():
        res.result = pr.FAIL_DUPLICATE_NICKNAME.Value()
        return res

    character = Character(
        user_id=ctx.sessions[ctx.transport]["user"].id,
        nickname=req.nickName,
        gender=Gender(req.gender),
        character_class=CharacterClass(req.characterClass)
    )
    character.save()

    return res


def delete_character(ctx, req):
    """Occurs when the user attempts to delete a character."""
    pr = pc.PacketResult

    res = acc.SS2C_ACCOUNT_CHARACTER_DELETE_RES()
    res.result = pr.SUCCESS.Value()

    query = db.query(Character).filter_by(id=req.characterId).first()

    # Prevents characters from maliciously deleting others characters.
    if query.user_id != ctx.sessions[ctx.transport]["user"].id:
        res.result = pc.FAIL_GENERAL.Value()
        return res

    query.delete()

    return res


def character_info(ctx):
    """Communication that occurs when the user loads into the lobby/tavern.
    Sends the game the relevant character information to be rendered in-game."""
    res = lb.SS2C_LOBBY_CHARACTER_INFO_RES()
    res.result = 1

    query = db.query(Character).filter_by(user_id=ctx.sessions[ctx.transport]["user"].id).all()

    nick = char.SACCOUNT_NICKNAME(
        originalNickName=query.nickname,
        streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
    )

    info = char.SCHARACTER_INFO(
        accountId="1",
        nickName=nick,
        characterClass=query.character_class,
        characterId=str(query.id),
        gender=query.gender,
        level=query.level
    )

    info.CharacterItemList.extend([
        items.generate_helm(), items.generate_torch(), items.generate_lantern(), 
        items.generate_sword(), items.generate_pants(), items.generate_tunic(), 
        items.generate_bandage()
    ])

    res.characterDataBase.CopyFrom(info)

    return res
