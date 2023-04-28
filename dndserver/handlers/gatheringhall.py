from dndserver.database import db
from dndserver.protos.GatheringHall import (
    SC2S_GATHERING_HALL_CHANNEL_LIST_REQ, SS2C_GATHERING_HALL_CHANNEL_LIST_RES,
    SC2S_GATHERING_HALL_CHANNEL_SELECT_REQ, SS2C_GATHERING_HALL_CHANNEL_SELECT_RES,
    SC2S_GATHERING_HALL_TARGET_EQUIPPED_ITEM_REQ, SS2C_GATHERING_HALL_TARGET_EQUIPPED_ITEM_RES
    )

from dndserver.sessions import sessions
from dndserver.handlers import character

def gathering_hall_channel_list(ctx, msg):
    req = SC2S_GATHERING_HALL_CHANNEL_LIST_REQ()
    req.ParseFromString(msg)
    channel = SGATHERING_HALL_CHANNEL(
        channelIndex=sessions[ctx.transport].gatheringhall.channel_index,
        channelId=sessions[ctx.transport].gatheringhall.channel_index,
        memberCount=sessions[ctx.transport].party.players,
        groupIndex=sessions[ctx.transport].gatheringhall.channel_index
    )
    res = SS2C_GATHERING_HALL_CHANNEL_LIST_RES(channels=channel)
    return res

def gathering_hall_select_channel(ctx, msg):
    req = SC2S_GATHERING_HALL_CHANNEL_SELECT_REQ()
    req.ParseFromString(msg)
    sessions[ctx.transport].gatheringhall.channel_index = req.channelIndex
    res = SS2C_GATHERING_HALL_CHANNEL_SELECT_RES(result=pc.SUCCESS)
    return res

def gathering_hall_equip(ctx, msg):
    req = SC2S_GATHERING_HALL_TARGET_EQUIPPED_ITEM_REQ()
    req.ParseFromString(msg)

    query = db.query(Character).filter_by(id=req.characterId).first()
    charinfo = SCHARACTER_GATHERING_HALL_INFO(
        accountId=req.accountId,
            nickName=SACCOUNT_NICKNAME(
                originalNickName=query.nickname,
                streamingModeNickName=query.streaming_nickname
            )
        )
    res = SS2C_GATHERING_HALL_TARGET_EQUIPPED_ITEM_RES(result=pc.SUCCESS, equippedItems=None, characterInfo=charinfo)
    return res
