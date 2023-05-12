from dndserver.protos import PacketCommand as pc
from dndserver.protos.Trade import (
    SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES,
    STRADE_MEMBERSHIP_REQUIREMENT,
    SS2C_TRADE_MEMBERSHIP_RES,
    SS2C_TRADE_CHANNEL_LIST_RES,
    STRADE_CHANNEL,
    SS2C_TRADE_CHANNEL_SELECT_RES,
    SS2C_TRADE_CHANNEL_CHAT_RES,
    STRADE_CHAT_S2C,
    SC2S_TRADE_CHANNEL_CHAT_REQ,
    SS2C_TRADE_CHANNEL_EXIT_RES,
)
from dndserver.protos.Chat import SCHATDATA, SCHATDATA_PIECE, SCHATDATA_PIECE_ITEM, SCHATDATA_PIECE_ITEM_PROPERTY
from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.protos.Defines import Define_Trade


def get_trade_reqs(ctx, msg):
    return SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES(
        # TODO: Unsure what these values are actually supposed to look like.
        requirements=[
            STRADE_MEMBERSHIP_REQUIREMENT(
                memberShipType=Define_Trade.Requirement_Type.MINIMUM_LEVEL, memberShipValue=5
            ),
            STRADE_MEMBERSHIP_REQUIREMENT(
                memberShipType=Define_Trade.Requirement_Type.INITIATION_FEE, memberShipValue=0
            ),
            STRADE_MEMBERSHIP_REQUIREMENT(
                memberShipType=Define_Trade.Requirement_Type.COST_PER_TRADE, memberShipValue=15
            ),
        ]
    )


def get_trade_channels(ctx, msg):
    return SS2C_TRADE_CHANNEL_LIST_RES(
        isTrader=1,
        channels=[
            STRADE_CHANNEL(
                index=1,
                channelName="ChatRoomData:Id_ChatRoom_Trade_Barbarian",
                memberCount=219,
                roomType=1,
                groupIndex=1,
            )
        ],
    )


def select_trade_channel(ctx, msg):
    return SS2C_TRADE_CHANNEL_SELECT_RES(result=pc.SUCCESS)


def chat_request(ctx, msg):
    req = SC2S_TRADE_CHANNEL_CHAT_REQ()
    req.ParseFromString(msg)

    chat_type = req.chat.chatType
    # target_account_id = req.chat.targetAccountId #currently unused
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

    nickname = SACCOUNT_NICKNAME(originalNickName="Krofty", streamingModeNickName="")
    chat_data = SCHATDATA()
    chat_data.accountId = "1"
    chat_data.characterId = "1"
    chat_data.nickname.CopyFrom(nickname)
    chat_data.partyId = "1"
    chat_data.chatDataPieceArray.append(chat_piece)

    chat_trade = STRADE_CHAT_S2C()
    chat_trade.index = 1
    chat_trade.chatType = chat_type
    chat_trade.time = 1
    chat_trade.chatData.CopyFrom(chat_data)

    return SS2C_TRADE_CHANNEL_CHAT_RES(result=pc.SUCCESS, chats=[chat_trade])


def exit(ctx, msg):
    return SS2C_TRADE_CHANNEL_EXIT_RES(result=pc.SUCCESS)


def process_membership(ctx, msg):
    return SS2C_TRADE_MEMBERSHIP_RES(result=pc.SUCCESS)
