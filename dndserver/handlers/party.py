from dndserver.enums import CharacterClass, Gender
from dndserver.objects.items import (
    generate_bandage,
    generate_helm,
    generate_lantern,
    generate_pants,
    generate_roundshield,
    generate_sword,
    generate_torch,
    generate_tunic,
)
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_PARTY_INFO
from dndserver.protos.Party import (
    SC2S_PARTY_INVITE_ANSWER_REQ,
    SC2S_PARTY_INVITE_REQ,
    SS2C_PARTY_INVITE_ANSWER_RES,
    SS2C_PARTY_INVITE_ANSWER_RESULT_NOT,
    SS2C_PARTY_INVITE_NOT,
    SS2C_PARTY_INVITE_RES,
    SS2C_PARTY_MEMBER_INFO_NOT,
)
from dndserver.utils import get_party_by_account_id, get_user_by_account_id, get_user_by_nickname, make_header


def party_invite(ctx, msg):
    """Occurs when a user sends a party to another user."""
    # message SC2S_PARTY_INVITE_REQ {
    #   .DC.Packet.SACCOUNT_NICKNAME findNickName = 1;
    #   string findAccountId = 2;
    #   string findCharacterId = 3;
    # }
    req = SC2S_PARTY_INVITE_REQ()
    req.ParseFromString(msg)
    res = SS2C_PARTY_INVITE_RES(result=pc.SUCCESS)
    send_invite_notification(ctx, req)
    return res


def accept_invite(ctx, msg):
    """Occurs when a user accepts a party invite."""
    # req.returnAccountId == inviter
    req = SC2S_PARTY_INVITE_ANSWER_REQ()
    req.ParseFromString(msg)

    res = SS2C_PARTY_INVITE_ANSWER_RES(result=pc.SUCCESS)

    # send a notification to the inviter that the invitee accepted
    send_accept_notification(ctx, req)

    # delete empty party if the user joining the party was the only member
    if len(sessions[ctx.transport].party.players) == 1:
        del sessions[ctx.transport].party

    # add user to the inviters party object
    party = get_party_by_account_id(
        int(req.returnAccountId)
    )  # todo: we're storing the first player as a transport and the next as a user object
    party.add_member(sessions[ctx.transport])

    # set the invitees party to the inviters party
    sessions[ctx.transport].party = party

    for user in party.players:
        send_party_info_notification(party, user)

    return res


def send_invite_notification(ctx, req):
    notify = SS2C_PARTY_INVITE_NOT(
        InviteeNickName=SACCOUNT_NICKNAME(
            originalNickName=sessions[ctx.transport].character.nickname,
            streamingModeNickName=sessions[ctx.transport].character.streaming_nickname,
            karmaRating=sessions[ctx.transport].character.karma_rating,
        ),
        InviteeAccountId=str(sessions[ctx.transport].account.id),
        InviteeCharacterId=str(sessions[ctx.transport].character.id),
    )

    # TODO: This can probably be refactored in a cleaner way in protocol.py.
    header = make_header(notify)
    transport, _ = get_user_by_nickname(nickname=req.findNickName.originalNickName)
    transport.write(header + notify.SerializeToString())


def send_accept_notification(ctx, req):
    transport, _ = get_user_by_account_id(int(req.returnAccountId))
    notify = SS2C_PARTY_INVITE_ANSWER_RESULT_NOT(
        nickName=SACCOUNT_NICKNAME(
            originalNickName=sessions[ctx.transport].character.nickname,
            streamingModeNickName=sessions[ctx.transport].character.streaming_nickname,
            karmaRating=sessions[ctx.transport].character.karma_rating,
        ),
        inviteResult=pc.SUCCESS,
    )
    header = make_header(notify)
    transport.write(header + notify.SerializeToString())


def send_party_info_notification(party, user):
    # message SS2C_PARTY_MEMBER_INFO_NOT {
    #     repeated .DC.Packet.SCHARACTER_PARTY_INFO playPartyUserInfoData = 1;
    # }

    #     message SCHARACTER_PARTY_INFO {
    #   string accountId = 1;
    #   .DC.Packet.SACCOUNT_NICKNAME nickName = 2;
    #   string characterClass = 3;
    #   string characterId = 4;
    #   uint32 gender = 5;
    #   uint32 level = 6;
    #   uint32 isPartyLeader = 7;
    #   uint32 isReady = 8;
    #   uint32 isInGame = 9;
    #   repeated .DC.Packet.SItem equipItemList = 10;
    #   uint32 partyIdx = 11;
    # }

    notify = SS2C_PARTY_MEMBER_INFO_NOT()
    for user in party.players:
        nick = SACCOUNT_NICKNAME(
            originalNickName=user.character.nickname,
            streamingModeNickName=user.character.streaming_nickname,
            karmaRating=user.character.karma_rating,
        )
        info = SCHARACTER_PARTY_INFO()
        info.accountId = str(user.account.id)
        info.nickName.CopyFrom(nick)
        info.characterClass = CharacterClass(user.character.character_class).value
        info.characterId = str(user.character.id)
        info.gender = Gender(user.character.gender).value
        info.level = user.character.level
        info.isPartyLeader = True if party.leader == user else False
        info.isReady = 0  # Need to unhardcode these 2
        info.isInGame = 0
        info.equipItemList.extend(
            [
                generate_helm(),
                generate_torch(),
                generate_roundshield(),
                generate_lantern(),
                generate_sword(),
                generate_pants(),
                generate_tunic(),
                generate_bandage(),
            ]
        )
        info.partyIdx = party.id
        notify.playPartyUserInfoData.append(info)

    header = make_header(notify)
    for user in party.players:
        transport, _ = get_user_by_account_id(user.account.id)
        transport.write(header + notify.SerializeToString())
        # header = make_header(notify)
        # transport.write(header + notify.SerializeToString())

    # SCHARACTER_PARTY_INFO {
    #     string accountId = 1;
    #     .DC.Packet.SACCOUNT_NICKNAME nickName = 2;
    #     string characterClass = 3;
    #     string characterId = 4;
    #     uint32 gender = 5;
    #     uint32 level = 6;
    #     uint32 isPartyLeader = 7;
    #     uint32 isReady = 8;
    #     uint32 isInGame = 9;
    #     repeated .DC.Packet.SItem equipItemList = 10;
    #     uint32 partyIdx = 11;
    # }
