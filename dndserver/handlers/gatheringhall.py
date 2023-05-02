from dndserver.database import db
from dndserver.models import Character, ChatLog
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_GATHERING_HALL_INFO
from dndserver.protos.Chat import SCHATDATA, SCHATDATA_PIECE, SCHATDATA_PIECE_ITEM, SCHATDATA_PIECE_ITEM_PROPERTY
from dndserver.protos.GatheringHall import (
    SC2S_GATHERING_HALL_CHANNEL_CHAT_REQ,
    SC2S_GATHERING_HALL_CHANNEL_EXIT_REQ,
    SC2S_GATHERING_HALL_CHANNEL_LIST_REQ,
    SC2S_GATHERING_HALL_CHANNEL_SELECT_REQ,
    SC2S_GATHERING_HALL_TARGET_EQUIPPED_ITEM_REQ,
    SGATHERING_HALL_CHANNEL,
    SGATHERING_HALL_CHAT_S2C,
    SS2C_GATHERING_HALL_CHANNEL_CHAT_RES,
    SS2C_GATHERING_HALL_CHANNEL_EXIT_RES,
    SS2C_GATHERING_HALL_CHANNEL_LIST_RES,
    SS2C_GATHERING_HALL_CHANNEL_SELECT_RES,
    SS2C_GATHERING_HALL_TARGET_EQUIPPED_ITEM_RES,
)

channels = {}
for i in range(1, 7):
    channels[f"channel{i}"] = {"index": i, "clients": []}


def gathering_hall_channel_list(ctx, msg):
    req = SC2S_GATHERING_HALL_CHANNEL_LIST_REQ()
    req.ParseFromString(msg)
    res = SS2C_GATHERING_HALL_CHANNEL_LIST_RES()
    for ch in channels:
        res.channels.append(
            SGATHERING_HALL_CHANNEL(
                channelIndex=channels[ch]["index"],
                channelId=f"{channels[ch]['index']}",
                memberCount=len(channels[ch]["clients"]),
                groupIndex=channels[ch]["index"],
            )
        )
    return res


def gathering_hall_select_channel(ctx, msg):
    req = SC2S_GATHERING_HALL_CHANNEL_SELECT_REQ()
    req.ParseFromString(msg)
    channels[f"channel{req.channelIndex}"]["clients"].append(ctx)
    return SS2C_GATHERING_HALL_CHANNEL_SELECT_RES(result=pc.SUCCESS)


def gathering_hall_equip(ctx, msg):
    req = SC2S_GATHERING_HALL_TARGET_EQUIPPED_ITEM_REQ()
    req.ParseFromString(msg)
    query = db.query(Character).filter_by(id=req.characterId).first()
    charinfo = SCHARACTER_GATHERING_HALL_INFO(
        accountId=req.accountId,
        nickName=SACCOUNT_NICKNAME(originalNickName=query.nickname, streamingModeNickName=query.streaming_nickname),
    )
    return SS2C_GATHERING_HALL_TARGET_EQUIPPED_ITEM_RES(result=pc.SUCCESS, equippedItems=None, characterInfo=charinfo)


def gathering_hall_channel_exit(ctx, msg):
    req = SC2S_GATHERING_HALL_CHANNEL_EXIT_REQ()
    req.ParseFromString(msg)

    # Find the client's channel
    current_channel = None
    for ch in channels:
        if ctx in channels[ch]["clients"]:
            current_channel = ch
            break

    # If a channel was found, remove the client from the channel
    if current_channel:
        channels[current_channel]["clients"].remove(ctx)
    res = SS2C_GATHERING_HALL_CHANNEL_EXIT_RES(result=pc.SUCCESS)

    # Refreshes user count
    ctx.reply(gathering_hall_channel_list(ctx, msg))

    return res


def broadcast_chat(ctx, msg):
    # Broadcast the message to other clients
    res = SS2C_GATHERING_HALL_CHANNEL_CHAT_RES(result=pc.SUCCESS, chats=msg)

    # Find the client's channel
    current_channel = None
    for ch in channels:
        if ctx in channels[ch]["clients"]:
            current_channel = ch
            break

    if current_channel:
        for client in channels[current_channel]["clients"]:
            # Send the chat message to each client in the channel except the sender
            if client != ctx:
                client.reply(res)


def chat(ctx, msg):
    req = SC2S_GATHERING_HALL_CHANNEL_CHAT_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(user_id=f"{sessions[ctx.transport].account.id}").first()

    chat_type = req.chat.chatType
    chat_str = req.chat.chatData.chatDataPieceArray[0].chatStr
    uid = req.chat.chatData.chatDataPieceArray[0].chatDataPieceItem.uid
    iid = req.chat.chatData.chatDataPieceArray[0].chatDataPieceItem.iid
    pp_list = req.chat.chatData.chatDataPieceArray[0].chatDataPieceItem.pp

    property_list = []
    for pp in pp_list:
        property_list.append(SCHATDATA_PIECE_ITEM_PROPERTY(pid=pp.pid, pv=pp.pv))

    chat_piece_item_obj = SCHATDATA_PIECE_ITEM(uid=uid, iid=iid, pp=property_list)

    chat_piece = SCHATDATA_PIECE()
    chat_piece.chatStr = chat_str
    chat_piece.chatDataPieceItem.CopyFrom(chat_piece_item_obj)

    nickName = SACCOUNT_NICKNAME(originalNickName=query.nickname, streamingModeNickName=query.streaming_nickname)
    chat_data = SCHATDATA()
    chat_data.accountId = f"{sessions[ctx.transport].account.id}"
    chat_data.characterId = f"{sessions[ctx.transport].character.id}"
    chat_data.nickname.CopyFrom(nickName)
    chat_data.partyId = f"{sessions[ctx.transport].party.id}"
    chat_data.chatDataPieceArray.append(chat_piece)

    chat_hall = SGATHERING_HALL_CHAT_S2C()
    chat_hall.chatIndex = 1
    chat_hall.chatType = chat_type
    chat_hall.time = 1
    chat_hall.chatData.CopyFrom(chat_data)

    log_msg = ChatLog(
        message=req.chat.chatData.chatDataPieceArray[0].chatStr,
        user_id=f"{sessions[ctx.transport].account.id}",
        chat_type=chat_type,
        chat_index=1,
    )
    log_msg.save()

    # Broadcast the message to other clients
    broadcast_chat(ctx, [chat_hall])

    return SS2C_GATHERING_HALL_CHANNEL_CHAT_RES(result=pc.SUCCESS, chats=[chat_hall])
