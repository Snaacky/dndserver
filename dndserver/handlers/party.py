from dndserver.enums.classes import CharacterClass, Gender
from dndserver.handlers import inventory
from dndserver.handlers import character as Char
from dndserver.objects.party import Party
from dndserver.persistent import parties, sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Defines import Define_Item, Define_Common
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_PARTY_INFO
from dndserver.protos.Party import (
    SC2S_PARTY_EXIT_REQ,
    SC2S_PARTY_INVITE_ANSWER_REQ,
    SC2S_PARTY_INVITE_REQ,
    SS2C_PARTY_EXIT_RES,
    SS2C_PARTY_INVITE_ANSWER_RES,
    SS2C_PARTY_INVITE_ANSWER_RESULT_NOT,
    SS2C_PARTY_INVITE_NOT,
    SS2C_PARTY_INVITE_RES,
    SS2C_PARTY_MEMBER_INFO_NOT,
    SC2S_PARTY_READY_REQ,
    SS2C_PARTY_READY_RES,
    SS2C_PARTY_LOCATION_UPDATE_NOT,
)
from dndserver.utils import get_party, get_user, make_header


def party_invite(ctx, msg):
    """Occurs when a user sends a party to another user."""
    req = SC2S_PARTY_INVITE_REQ()
    req.ParseFromString(msg)
    send_invite_notification(ctx, req)
    return SS2C_PARTY_INVITE_RES(result=pc.SUCCESS)


def accept_invite(ctx, msg):
    """Occurs when a user accepts a party invite."""
    # req.returnAccountId == inviter
    req = SC2S_PARTY_INVITE_ANSWER_REQ()
    req.ParseFromString(msg)

    # send a notification to the inviter that the invitee accepted
    send_accept_notification(ctx, req)

    # delete empty party if the user joining the party was the only member
    if len(sessions[ctx.transport].party.players) == 1:
        del parties[sessions[ctx.transport].party.id - 1]
        del sessions[ctx.transport].party

    # add user to the inviters party object
    party = get_party(account_id=int(req.returnAccountId))
    party.add_member(sessions[ctx.transport])

    # set the invitees party to the inviters party
    sessions[ctx.transport].party = party

    send_party_info_notification(party)

    return SS2C_PARTY_INVITE_ANSWER_RES(result=pc.SUCCESS)


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
    transport, _ = get_user(nickname=req.findNickName.originalNickName)
    transport.write(header + notify.SerializeToString())


def send_accept_notification(ctx, req):
    transport, _ = get_user(account_id=int(req.returnAccountId))
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


def send_party_info_notification(party):
    """Notification sent to all players in the lobby that updates the current party player list."""
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
        info.isReady = user.state.is_ready
        info.isInGame = user.state.location == Define_Common.MetaLocation.INGAME

        for item, attribute in inventory.get_all_items(user.character.id, Define_Item.InventoryId.EQUIPMENT):
            info.equipItemList.extend([Char.item_to_proto_item(item, attribute)])

        info.partyIdx = party.id
        notify.playPartyUserInfoData.append(info)

    header = make_header(notify)
    for user in party.players:
        transport, _ = get_user(account_id=user.account.id)
        transport.write(header + notify.SerializeToString())


def send_party_location_notification(party, session):
    """Notification send the other party members that updates the location of the provided user"""
    notify = SS2C_PARTY_LOCATION_UPDATE_NOT()
    notify.accountId = str(session.account.id)
    notify.characterId = str(session.character.id)
    notify.updateLocation = session.state.location

    header = make_header(notify)
    for user in party.players:
        # check if we have the user that started the update. No need to send it to that user
        if user.account.id == session.account.id:
            continue

        transport, _ = get_user(account_id=user.account.id)
        transport.write(header + notify.SerializeToString())


def leave_party(ctx, msg):
    """Occurs when a user leaves the party."""
    req = SC2S_PARTY_EXIT_REQ()
    req.ParseFromString(msg)

    user_leaving = sessions[ctx.transport]

    party = get_party(account_id=user_leaving.account.id)
    if not party:
        return SS2C_PARTY_EXIT_RES(result=pc.FAIL_GENERAL)

    # Party leader needs to be passed if the leader is leaving..
    if party.leader == user_leaving:
        for user in party.players:
            if user != user_leaving:
                party.leader = user
                break

    party.remove_member(user_leaving)
    new_party = Party(player_1=sessions[ctx.transport])
    new_party.leader = user_leaving
    parties.append(new_party)
    sessions[ctx.transport].party = new_party

    send_party_info_notification(party)
    send_party_info_notification(new_party)
    return SS2C_PARTY_EXIT_RES(result=pc.SUCCESS)


def set_ready_state(ctx, msg):
    """Occurs when a user presses the ready button in a party."""
    req = SC2S_PARTY_READY_REQ()
    req.ParseFromString(msg)

    # change the state of the user
    sessions[ctx.transport].state.is_ready = req.isReady

    # notify the party with the change to the ready state
    party = get_party(account_id=sessions[ctx.transport].account.id)
    send_party_info_notification(party)

    return SS2C_PARTY_READY_RES(result=pc.SUCCESS)
