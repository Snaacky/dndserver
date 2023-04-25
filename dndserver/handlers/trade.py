import random

from dndserver.protos import PacketCommand as pc
from dndserver.protos.Trade import (SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES, STRADE_MEMBERSHIP_REQUIREMENT,
                                    SS2C_TRADE_MEMBERSHIP_RES, SS2C_TRADE_CHANNEL_LIST_RES, STRADE_CHANNEL,
                                    SS2C_TRADE_CHANNEL_SELECT_RES, SS2C_TRADE_CHANNEL_CHAT_RES, STRADE_CHAT_S2C,)
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
    return SCHATDATA_PIECE_ITEM_PROPERTY(pid="DesignDataItem:Id_Item_Torch_0001", pv=1)


def chat_piece_item():
    return SCHATDATA_PIECE_ITEM(uid=1, iid="DesignDataItem:Id_Item_Torch_0001", pp=[chat_piece_item_property()], sp=[chat_piece_item_property()])


def chat_piece():
    data = SCHATDATA_PIECE()
    data.chatStr = "hi"
    data.chatDataPieceItem.CopyFrom(chat_piece_item())
    return data


def chat_data():
    nickname = SACCOUNT_NICKNAME(
        originalNickName="krofty",
        streamingModeNickName=f"Fighter#{random.randrange(1000000, 1700000)}"
    )

    data = SCHATDATA()
    data.accountId = "1"
    data.characterId = "1"
    data.nickname.CopyFrom(nickname)
    data.partyId = "1"
    data.chatDataPieceArray.append(chat_piece())
    return data


def chat_S2C():
    data = STRADE_CHAT_S2C()
    data.index = 1
    data.chatType = 1
    data.time = 219
    data.chatData.CopyFrom(chat_data())
    return data


def chat_request(ctx, msg):
    return SS2C_TRADE_CHANNEL_CHAT_RES(
        result=pc.SUCCESS,
        chats=[chat_S2C()]
    )


def process_membership(ctx, msg):
    return SS2C_TRADE_MEMBERSHIP_RES(result=pc.SUCCESS)
