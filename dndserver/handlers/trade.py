import random

from dndserver.protos import PacketCommand as pc
from dndserver.protos.Trade import (SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES, STRADE_MEMBERSHIP_REQUIREMENT,
                                    SS2C_TRADE_MEMBERSHIP_RES, SS2C_TRADE_CHANNEL_LIST_RES, STRADE_CHANNEL,
                                    SS2C_TRADE_CHANNEL_SELECT_RES, SS2C_TRADE_CHANNEL_CHAT_RES, STRADE_CHAT_S2C,
                                    SC2S_TRADE_CHANNEL_CHAT_REQ)
from dndserver.protos.Chat import (SCHATDATA, SCHATDATA_PIECE, SCHATDATA_PIECE_ITEM, 
                                   SCHATDATA_PIECE_ITEM_PROPERTY)
from dndserver.protos.Character import SACCOUNT_NICKNAME, SCHARACTER_INFO



def get_trade_reqs(ctx, msg):
    return SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES(
        # TODO: Unsure what these values are actually supposed to look like.
        requirements=[STRADE_MEMBERSHIP_REQUIREMENT(memberShipType=1, memberShipValue=1)]
    )


def get_trade_channels(ctx, msg):
    return SS2C_TRADE_CHANNEL_LIST_RES(isTrader=1, channels=[STRADE_CHANNEL(index=1, channelName="ChatRoomData:Id_ChatRoom_Trade_Barbarian", memberCount=219, roomType=1, groupIndex=1)])


def select_trade_channel(ctx, msg):
    return SS2C_TRADE_CHANNEL_SELECT_RES(result=pc.SUCCESS)


def chat_piece_item_property():
    return SCHATDATA_PIECE_ITEM_PROPERTY(pid="1", pv=1)


def chat_piece_item():
    return SCHATDATA_PIECE_ITEM(uid=1, iid="1")


def chat_piece(chatmsg):
    data = SCHATDATA_PIECE()
    data.chatStr = chatmsg
    #data.chatDataPieceItem.CopyFrom(chat_piece_item())
    return data


def chat_data(chatmsg):
    nickname = SACCOUNT_NICKNAME(
        originalNickName="krofty",
        streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
    )

    data = SCHATDATA()
    data.accountId = "1"
    data.characterId = "1"
    data.nickname.CopyFrom(nickname)
    data.partyId = "1"
    data.chatDataPieceArray.append(chat_piece(chatmsg))
    return data


def chat_S2C(chatmsg):
    data = STRADE_CHAT_S2C()
    data.index = 1
    data.chatType = 1
    data.time = 1
    data.chatData.CopyFrom(chat_data(chatmsg))
    return data


def chat_request(ctx, msg):
    req = SC2S_TRADE_CHANNEL_CHAT_REQ()
    req.ParseFromString(msg)
    print(req)
    chatmsg = req.chat.chatData.chatDataPieceArray[0].chatStr
    return SS2C_TRADE_CHANNEL_CHAT_RES(
        result=pc.SUCCESS,
        chats=[chat_S2C(chatmsg)]
    )


def process_membership(ctx, msg):
    return SS2C_TRADE_MEMBERSHIP_RES(result=pc.SUCCESS)
