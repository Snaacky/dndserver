import random

from dndserver.config import config
from dndserver.database import db
from dndserver.enums import CharacterClass, Gender
from dndserver.models import BlockedUser, Character
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_FRIEND_INFO, SBLOCK_CHARACTER
from dndserver.protos.Common import (
    SC2S_BLOCK_CHARACTER_REQ,
    SS2C_BLOCK_CHARACTER_RES,
    SC2S_UNBLOCK_CHARACTER_REQ,
    SS2C_UNBLOCK_CHARACTER_RES,
)
from dndserver.protos.Friend import SC2S_FRIEND_FIND_REQ, SS2C_FRIEND_FIND_RES, SS2C_FRIEND_LIST_ALL_RES
from dndserver.protos import PacketCommand as pc
from dndserver.sessions import sessions
from dndserver.utils import get_user_by_nickname


def list_friends(ctx, msg):
    nickname = SACCOUNT_NICKNAME()
    nickname.originalNickName = "gay"
    nickname.streamingModeNickName = f"Fighter#{random.randrange(1000000, 1700000)}"

    friend_info = SCHARACTER_FRIEND_INFO()
    friend_info.accountId = "2"
    friend_info.nickName.CopyFrom(nickname)
    friend_info.characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"
    friend_info.characterId = "2"
    friend_info.gender = 2
    friend_info.level = 12
    friend_info.locationStatus = 2
    friend_info.PartyMemeberCount = 1
    friend_info.PartyMaxMemeberCount = 3

    res = SS2C_FRIEND_LIST_ALL_RES()  # message SS2C_FRIEND_LIST_ALL_RES {
    res.friendInfoList.extend([friend_info])  # repeated .DC.Packet.SCHARACTER_FRIEND_INFO friendInfoList = 1;
    res.loopFlag = 1  # uint32 loopFlag = 2;
    res.totalUserCount = 2  # uint32 totalUserCount = 3;
    res.lobbyLocateCount = 1  # uint32 lobbyLocateCount = 4;
    res.dungeonLocateCount = 1  # uint32 dungeonLocateCount = 5

    return res


def find_user(ctx, msg):
    # message SC2S_FRIEND_FIND_REQ {
    #   .DC.Packet.SACCOUNT_NICKNAME nickName = 1;
    # }
    req = SC2S_FRIEND_FIND_REQ()
    req.ParseFromString(msg)

    res = SS2C_FRIEND_FIND_RES(result=pc.SUCCESS)

    # Makes it so users can't search for or invite themselves.
    if req.nickName.originalNickName == sessions[ctx.transport].character.nickname:
        return res

    _, session = get_user_by_nickname(nickname=req.nickName.originalNickName)
    if session:
        friend = SCHARACTER_FRIEND_INFO(
            accountId=str(session.account.id),
            nickName=SACCOUNT_NICKNAME(
                originalNickName=session.character.nickname,
                streamingModeNickName=session.character.streaming_nickname,
            ),
            characterClass=CharacterClass(session.character.character_class).value,
            characterId=str(session.character.id),
            gender=Gender(session.character.gender).value,
            level=session.character.level,
            locationStatus=1,  # TODO: Remove the hardcoding from these bottom 3.
            PartyMemeberCount=1,
            PartyMaxMemeberCount=3,
        )
        res.friendInfo.CopyFrom(friend)

    return res


def block_user(ctx, msg):
    """Occurs when a character blocks another character."""
    req = SC2S_BLOCK_CHARACTER_REQ()
    req.ParseFromString(msg)

    blocker = sessions[ctx.transport]
    blocked_char = db.query(Character).filter_by(id=req.targetCharacterId, user_id=req.targetAccountId).first()
    if not blocked_char:
        return SS2C_BLOCK_CHARACTER_RES(result=pc.FAIL_BLOCK_CHARACTER_NOT_FOUND)

    dupe = db.query(BlockedUser).filter_by(blocked_by=blocker.character.id, account_id=blocked_char.user_id).first()
    if dupe:
        return SS2C_BLOCK_CHARACTER_RES(result=pc.FAIL_BLOCK_CHARACTER_ALREADY)

    blocks = db.query(BlockedUser).filter_by(blocked_by=blocker.character.id).count()
    if blocks >= config.game.settings.max_blocked_characters:
        return SS2C_BLOCK_CHARACTER_RES(result=pc.FAIL_BLOCK_CHARACTER_LIMIT)

    user = BlockedUser(
        blocked_by=blocker.character.id,
        account_id=int(blocked_char.user_id),
        character_id=int(blocked_char.id),
        nickname=blocked_char.nickname,
        character_class=CharacterClass(blocked_char.character_class),
        gender=Gender(blocked_char.gender),
    )
    user.save()

    res = SS2C_BLOCK_CHARACTER_RES(
        result=pc.SUCCESS,
        targetCharacterInfo=SBLOCK_CHARACTER(
            accountId=str(blocked_char.user_id),
            characterId=str(blocked_char.id),
            nickName=SACCOUNT_NICKNAME(
                originalNickName=blocked_char.nickname,
                streamingModeNickName=blocked_char.streaming_nickname,
                karmaRating=blocked_char.karma_rating,
            ),
            characterClass=CharacterClass(blocked_char.character_class).value,
            gender=Gender(blocked_char.gender).value,
        ),
    )
    return res


def unblock_user(ctx, msg):
    req = SC2S_UNBLOCK_CHARACTER_REQ()
    req.ParseFromString(msg)

    query = (
        db.query(BlockedUser)
        .filter_by(blocked_by=sessions[ctx.transport].character.id, character_id=int(req.targetCharacterId))
        .first()
    )
    query.delete()

    return SS2C_UNBLOCK_CHARACTER_RES(result=pc.SUCCESS, targetCharacterId=req.targetCharacterId)


# def get_blocked_users(ctx, msg):
#     # message SC2S_BLOCK_CHARACTER_LIST_REQ {
#     # }
#     req = C2S_BLOCK_CHARACTER_LIST_REQ()
#     req.ParseFromString(msg)
#     # message SS2C_BLOCK_CHARACTER_LIST_RES {
#     #   repeated .DC.Packet.SBLOCK_CHARACTER blockCharacters = 1;
#     # }
#     res = S2C_BLOCK_CHARACTER_LIST_RES()
#     query = db.query(BlockedUser).filter_by(user_id=sessions[ctx.transport].account.id).all()

# message SBLOCK_CHARACTER {
#   string accountId = 1;
#   string characterId = 2;
#   .DC.Packet.SACCOUNT_NICKNAME nickName = 3;
#   string characterClass = 4;
#   uint32 gender = 5;
# }
