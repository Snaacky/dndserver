from datetime import datetime
from dndserver.enums.classes import CharacterClass, Gender
from dndserver.handlers import inventory
from dndserver.handlers import character as Char
from dndserver.objects.party import Party
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Defines import Define_Item, Define_Common
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_PARTY_INFO
from dndserver.protos.Chat import SCHATDATA, SCHATDATA_PIECE
from dndserver.protos.Party import (
    SC2S_PARTY_CHAT_REQ,
    SS2C_PARTY_CHAT_RES,
    SS2C_PARTY_CHAT_NOT,
    SC2S_PARTY_EXIT_REQ,
    SC2S_PARTY_INVITE_ANSWER_REQ,
    SC2S_PARTY_INVITE_REQ,
    SC2S_PARTY_MEMBER_KICK_REQ,
    SS2C_PARTY_EXIT_RES,
    SS2C_PARTY_INVITE_ANSWER_RES,
    SS2C_PARTY_INVITE_ANSWER_RESULT_NOT,
    SS2C_PARTY_INVITE_NOT,
    SS2C_PARTY_INVITE_RES,
    SS2C_PARTY_MEMBER_INFO_NOT,
    SC2S_PARTY_READY_REQ,
    SS2C_PARTY_READY_RES,
    SS2C_PARTY_LOCATION_UPDATE_NOT,
    SS2C_PARTY_MEMBER_KICK_RES,
)
from dndserver.utils import get_party, get_user, make_header


def has_online_players(party, exclude=[]):
    """Helper function to check if we have online players in a party excluding the exclude list"""
    for player in party.players:
        if player in exclude:
            continue

        if player.state.location != Define_Common.MetaLocation.OFFLINE:
            return True

    return False


def search_for_old_party(account_id):
    """Helper function to search for the old party of the user"""
    for session in sessions.values():
        if session.party is None:
            continue

        if len(session.party.players) <= 1:
            continue

        if session.party.leader != session:
            continue

        for player in session.party.players:
            if account_id == player.account.id:
                return session.party

    return None


def cleanup(ctx):
    """Helper function to cleanup the party after the user exits"""
    session = sessions[ctx.transport]

    # check if we have a valid user, state and have a party
    if not all([session.account, session.state, session.party]):
        return

    # change the state to offline
    session.state.location = Define_Common.MetaLocation.OFFLINE
    send_party_location_notification(session.party, session)

    # party leader needs to be passed if the leader is leaving
    if session.party.leader == session:
        for user in session.party.players:
            if user != session:
                session.party.leader = user
                break

    # update the party with the new party leader
    send_party_info_notification(session.party)


def party_invite(ctx, msg):
    """Occurs when a user sends a party to another user."""
    req = SC2S_PARTY_INVITE_REQ()
    req.ParseFromString(msg)

    party = get_party(account_id=int(req.findAccountId))
    # prevent inviter from sending invitation if invitee is already in the party
    if any(sessions[ctx.transport].account.id == player.account.id for player in party.players):
        return SS2C_PARTY_INVITE_RES(result=pc.FAIL_PARTY_INVITE_ALREADY_PARTY)

    send_invite_notification(ctx, req)
    return SS2C_PARTY_INVITE_RES(result=pc.SUCCESS)


def accept_invite(ctx, msg):
    """Occurs when a user accepts a party invite."""
    # req.returnAccountId == inviter
    # sessions[ctx.transport].account.id == invitee

    req = SC2S_PARTY_INVITE_ANSWER_REQ()
    req.ParseFromString(msg)

    # check if the user is already in the current party. This should never happen but catch it just in case.
    party = get_party(account_id=int(req.returnAccountId))
    if any(sessions[ctx.transport].account.id == player.account.id for player in party.players):
        # do not process the response if we are already in the party we are trying to join
        return SS2C_PARTY_INVITE_ANSWER_RES(result=pc.SUCCESS)

    # send a notification with the response to the inviter
    send_accept_notification(ctx, req)

    # check if the user accepted the invite
    if req.inviteResult != pc.SUCCESS:
        return SS2C_PARTY_INVITE_ANSWER_RES(result=pc.SUCCESS)

    # delete empty party if the user joining the party was the only member
    if len(sessions[ctx.transport].party.players) == 1:
        del sessions[ctx.transport].party

    # add user to the inviters party object
    party.add_member(sessions[ctx.transport])

    # set the invitees party to the inviters party
    sessions[ctx.transport].party = party

    send_party_info_notification(party)

    # send the location of everyone to everyone
    for user in party.players:
        send_party_location_notification(party, user)

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
    if transport is not None:
        transport.write(header + notify.SerializeToString())


def send_accept_notification(ctx, req):
    transport, _ = get_user(account_id=int(req.returnAccountId))
    if transport is None:
        return

    notify = SS2C_PARTY_INVITE_ANSWER_RESULT_NOT(
        nickName=SACCOUNT_NICKNAME(
            originalNickName=sessions[ctx.transport].character.nickname,
            streamingModeNickName=sessions[ctx.transport].character.streaming_nickname,
            karmaRating=sessions[ctx.transport].character.karma_rating,
        ),
        inviteResult=req.inviteResult,
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
        if transport is not None:
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
        if transport is not None:
            transport.write(header + notify.SerializeToString())


def leave_party(ctx, msg):
    """Occurs when a user leaves the party."""
    req = SC2S_PARTY_EXIT_REQ()
    req.ParseFromString(msg)

    user_leaving = sessions[ctx.transport]

    if not user_leaving.party:
        return SS2C_PARTY_EXIT_RES(result=pc.FAIL_GENERAL)

    # Party leader needs to be passed if the leader is leaving..
    if user_leaving.party.leader == user_leaving:
        for user in user_leaving.party.players:
            if user != user_leaving:
                user_leaving.party.leader = user
                break

    # leave the party and update the other users
    user_leaving.party.remove_member(user_leaving)
    send_party_info_notification(user_leaving.party)

    # give the leaving member a new party
    new_party = Party(player_1=user_leaving)
    new_party.leader = user_leaving
    user_leaving.party = new_party
    send_party_info_notification(new_party)
    return SS2C_PARTY_EXIT_RES(result=pc.SUCCESS)


def set_ready_state(ctx, msg):
    """Occurs when a user presses the ready button in a party."""
    req = SC2S_PARTY_READY_REQ()
    req.ParseFromString(msg)

    # change the state of the user
    sessions[ctx.transport].state.is_ready = req.isReady

    # notify the party with the change to the ready state
    send_party_info_notification(sessions[ctx.transport].party)

    return SS2C_PARTY_READY_RES(result=pc.SUCCESS)


def kick_member(ctx, msg):
    """Occurs when party leader clicks on Kick"""
    req = SC2S_PARTY_MEMBER_KICK_REQ()
    req.ParseFromString(msg)

    party = sessions[ctx.transport].party
    if party.leader != sessions[ctx.transport]:
        return SS2C_PARTY_MEMBER_KICK_RES(result=pc.FAIL_GENERAL)

    # search for the player we want to kick in the party
    kicked_user = None
    for player in party.players:
        if str(player.account.id) != req.accountId:
            continue
        kicked_user = player
        break

    # check if we have the player in the party
    if kicked_user is None:
        return SS2C_PARTY_MEMBER_KICK_RES(result=pc.FAIL_GENERAL)

    # kick the party member
    party.remove_member(kicked_user)

    # if the party member is offline we dont send a update to the user
    if kicked_user.state.location != Define_Common.MetaLocation.OFFLINE:
        new_party = Party(player_1=kicked_user)
        new_party.leader = kicked_user
        kicked_user.party = new_party
        send_party_info_notification(new_party)

    send_party_info_notification(party)
    return SS2C_PARTY_MEMBER_KICK_RES(result=pc.SUCCESS)


def broadcast_chat(ctx, msg):
    res = SS2C_PARTY_CHAT_NOT(chatData=msg, time=int(round(datetime.now().timestamp() * 1000)))
    header = make_header(res)

    for user in sessions[ctx.transport].party.players:
        transport, _ = get_user(account_id=user.account.id)
        if transport is not None:
            transport.write(header + res.SerializeToString())


def chat(ctx, msg):
    req = SC2S_PARTY_CHAT_REQ()
    req.ParseFromString(msg)
    character = sessions[ctx.transport].character
    chat_str = req.chatData.chatDataPieceArray[0].chatStr
    chat_piece = SCHATDATA_PIECE()
    chat_piece.chatStr = chat_str
    nickName = SACCOUNT_NICKNAME(
        originalNickName=character.nickname, streamingModeNickName=character.streaming_nickname
    )
    chat_data = SCHATDATA()
    chat_data.accountId = str(sessions[ctx.transport].account.id)
    chat_data.characterId = str(sessions[ctx.transport].character.id)
    chat_data.nickname.CopyFrom(nickName)
    chat_data.partyId = str(sessions[ctx.transport].party.id)
    chat_data.chatDataPieceArray.append(chat_piece)
    broadcast_chat(ctx, chat_data)
    return SS2C_PARTY_CHAT_RES(result=1)
