import random

from dndserver.enums import CharacterClass, Gender
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_FRIEND_INFO
from dndserver.protos.Friend import SC2S_FRIEND_FIND_REQ, SS2C_FRIEND_FIND_RES, SS2C_FRIEND_LIST_ALL_RES
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
