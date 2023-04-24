from dndserver.protos import Character as char
from dndserver.protos import Friend as friend
from dndserver.protos import Party as party


def list_friends(ctx, msg):
    nickname = char.SACCOUNT_NICKNAME()
    nickname.originalNickName = "gay"
    nickname.streamingModeNickName = "Fighter#11111"

    friend_info = char.SCHARACTER_FRIEND_INFO()
    friend_info.accountId = "2"
    friend_info.nickName.CopyFrom(nickname)
    friend_info.characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"
    friend_info.characterId = "2"
    friend_info.gender = 2
    friend_info.level = 12
    friend_info.locationStatus = 2
    friend_info.PartyMemeberCount = 1
    friend_info.PartyMaxMemeberCount = 3

    res = friend.SS2C_FRIEND_LIST_ALL_RES()    # message SS2C_FRIEND_LIST_ALL_RES {
    res.friendInfoList.extend([friend_info])   # repeated .DC.Packet.SCHARACTER_FRIEND_INFO friendInfoList = 1;
    res.loopFlag = 1                           # uint32 loopFlag = 2;
    res.totalUserCount = 2                     # uint32 totalUserCount = 3;
    res.lobbyLocateCount = 1                   # uint32 lobbyLocateCount = 4;
    res.dungeonLocateCount = 1                 # uint32 dungeonLocateCount = 5

    return res


def find_user(ctx, msg):
    nick = char.SACCOUNT_NICKNAME()
    nick.originalNickName = "krofty"
    nick.streamingModeNickName = "Fighter#00321"
    nick.karmaRating = 666

    friend_info = char.SCHARACTER_FRIEND_INFO()
    friend_info.accountId = "2"
    friend_info.nickName.CopyFrom(nick)
    friend_info.characterClass = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"
    friend_info.characterId = "2"
    friend_info.gender = 2
    friend_info.level = 12
    friend_info.locationStatus = 2
    friend_info.PartyMemeberCount = 1
    friend_info.PartyMaxMemeberCount = 3

    res = friend.SS2C_FRIEND_FIND_RES()
    res.result = 1
    res.friendInfo.CopyFrom(friend_info)
    return res


def party_invite(ctx, msg):
    # message SC2S_PARTY_INVITE_REQ {
    # .DC.Packet.SACCOUNT_NICKNAME findNickName = 1;
    # string findAccountId = 2;
    # string findCharacterId = 3;
    # }
    res = party.SS2C_PARTY_INVITE_RES()
    res.result = 1
    return res


def party_invite_notify(ctx, msg):
    res = party.SS2C_PARTY_INVITE_NOT()

    nick = char.SACCOUNT_NICKNAME()
    nick.originalNickName = "krofty"
    nick.streamingModeNickName = "Fighter#00321"
    nick.karmaRating = 666

    res.InviteeAccountId = "1"
    res.InviteeCharacterId = "1"
    res.InviteeNickName.CopyFrom(nick)
    return res

    # message SS2C_PARTY_INVITE_RES {
    # uint32 result = 1;
    # }

    # message SS2C_PARTY_INVITE_NOT {
    # .DC.Packet.SACCOUNT_NICKNAME InviteeNickName = 1;
    # string InviteeAccountId = 2;
    # string InviteeCharacterId = 3;
    # }

    # message SC2S_PARTY_INVITE_ANSWER_REQ {
    # uint32 inviteResult = 1;
    # string returnAccountId = 2;
    # }

    # message SS2C_PARTY_INVITE_ANSWER_RES {
    # uint32 result = 1;
    # }

    # message SS2C_PARTY_INVITE_ANSWER_RESULT_NOT {
    # .DC.Packet.SACCOUNT_NICKNAME nickName = 1;
    # uint32 inviteResult = 2;
    # }
    return
