import arrow

from dndserver.database import db
from dndserver.handlers import inventory
from dndserver.handlers import character as HCharacter
from dndserver.models import Item, ItemAttribute
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Trade import (
    SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES,
    STRADE_MEMBERSHIP_REQUIREMENT,
    SS2C_TRADE_MEMBERSHIP_RES,
    SS2C_TRADE_CHANNEL_LIST_RES,
    STRADE_CHANNEL,
    SC2S_TRADE_CHANNEL_SELECT_REQ,
    SS2C_TRADE_CHANNEL_SELECT_RES,
    SS2C_TRADE_CHANNEL_CHAT_RES,
    STRADE_CHAT_S2C,
    SC2S_TRADE_CHANNEL_CHAT_REQ,
    SS2C_TRADE_CHANNEL_EXIT_RES,
    SC2S_TRADE_REQUEST_REQ,
    SS2C_TRADE_REQUEST_RES,
    SS2C_TRADE_REQUEST_NOT,
    SC2S_TRADE_ANSWER_REQ,
    SS2C_TRADE_ANSWER_RES,
    SS2C_TRADE_ANSWER_REFUSAL_NOT,
    SS2C_TRADING_BEGIN_NOT,
    STRADING_USER_INFO,
    SC2S_TRADING_ITEM_UPDATE_REQ,
    SS2C_TRADING_ITEM_UPDATE_RES,
    SC2S_TRADING_CHAT_REQ,
    SS2C_TRADING_CHAT_RES,
    SS2C_TRADING_CLOSE_RES,
    SS2C_TRADE_CHANNEL_USER_UPDATE_NOT,
    STRADE_CHANNEL_USER_UPDATE_INFO,
    SC2S_TRADING_READY_REQ,
    SS2C_TRADING_READY_RES,
    SS2C_TRADING_READY_NOT,
    SS2C_TRADING_CONFIRM_NOT,
    SS2C_TRADING_CONFIRM_CANCEL_RES,
    SC2S_TRADING_CONFIRM_READY_REQ,
    SS2C_TRADING_CONFIRM_READY_RES,
    SS2C_TRADING_CONFIRM_READY_NOT,
    SS2C_TRADING_RESULT_NOT,
)
from dndserver.protos.Chat import SCHATDATA, SCHATDATA_PIECE, SCHATDATA_PIECE_ITEM, SCHATDATA_PIECE_ITEM_PROPERTY
from dndserver.protos.Character import SCHARACTER_TRADE_INFO
from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.protos.Defines import Define_Trade, Define_Message, Define_Item
from dndserver.objects.trade import Trade, TradeParty
from dndserver.persistent import trades
from dndserver.enums import classes

trade_fee = 15
initial_trade_fee = 25

channel_names = ["Fighter", "Barbarian", "Rogue", "Ranger", "Wizard", "Cleric", "Bard", "Utility", "Misc"]
channels = []

# create the channels on startup
for index, name in enumerate(channel_names):
    channels.append({"name": name, "index": index + 1, "clients": []})


def get_current_channel(ctx):
    """Helper function to get the current channel the user is in"""
    for ch in channels:
        if ctx in ch["clients"]:
            return ch

    return None


def get_user_in_channel(channel, account_id):
    """Helper function to find the transport of a account id"""
    # search for the other player we want to send the notification to
    for client in channel["clients"]:
        if sessions[client.transport].account.id != int(account_id):
            continue

        return client

    return None


def find_trade(ctx):
    """Helper function to find the current trade"""
    for trade in trades:
        if trade.user0.ctx == ctx:
            return (trade, trade.user0, trade.user1)
        elif trade.user1.ctx == ctx:
            return (trade, trade.user1, trade.user0)

    return (None, None, None)


def broadcast_chat(ctx, msg):
    """Helper function to broadcast a chat message to all the participants in a channel"""
    # Broadcast the message to other clients
    res = SS2C_TRADE_CHANNEL_CHAT_RES(result=pc.SUCCESS, chats=msg)

    # Find the client's channel
    channel = get_current_channel(ctx)

    if channel:
        for client in channel["clients"]:
            # Send the chat message to each client in the channel except the sender
            if client != ctx:
                client.reply(res)


def leave_channel(ctx, channel):
    """Helper function to have a player 'leave' a channel"""
    # remove the player from the client list
    channel["clients"].remove(ctx)
    char = sessions[ctx.transport].character

    # send a notification to all the players in the channel
    for client in channel["clients"]:
        client.reply(
            SS2C_TRADE_CHANNEL_USER_UPDATE_NOT(
                updates=[
                    STRADE_CHANNEL_USER_UPDATE_INFO(
                        trader=get_trader_info(char, str(sessions[ctx.transport].account.id)),
                        updateFlag=Define_Message.UpdateFlag.DELETE,
                    )
                ]
            )
        )


def cleanup(ctx):
    """Helper function to cleanup anything left when the client crashes or alt-f4s"""
    # check if the user is in any active trades
    trade, _, other = find_trade(ctx)

    # if we found a trade cancel everything
    if trade:
        other.ctx.reply(SS2C_TRADING_CONFIRM_CANCEL_RES(result=pc.SUCCESS))
        other.ctx.reply(SS2C_TRADING_CLOSE_RES(result=pc.SUCCESS))

    # find the client's channel
    channel = get_current_channel(ctx)

    if channel:
        leave_channel(ctx, channel)


def get_trader_info(char, account_id):
    """Helper function to create trader information from the character and account id"""
    nickname = SACCOUNT_NICKNAME(originalNickName=char.nickname, streamingModeNickName=char.streaming_nickname)

    trader = SCHARACTER_TRADE_INFO()
    trader.accountId = account_id
    trader.nickName.CopyFrom(nickname)
    trader.characterClass = classes.CharacterClass(char.character_class).value
    trader.characterId = str(char.id)
    trader.gender = classes.Gender(char.gender).value
    trader.level = char.level
    trader.characterLocation = 1

    return trader


def get_trading_info(ctx):
    """Helper function to get the trading info for a user"""
    char = sessions[ctx.transport].character
    nickname = SACCOUNT_NICKNAME(originalNickName=char.nickname, streamingModeNickName=char.streaming_nickname)

    trader = STRADING_USER_INFO()
    trader.nickName.CopyFrom(nickname)
    trader.accountId = str(sessions[ctx.transport].account.id)

    return trader


def create_chat_data(ctx, req):
    """Helper function to create chat data"""
    character = sessions[ctx.transport].character

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

    nickName = SACCOUNT_NICKNAME(
        originalNickName=character.nickname, streamingModeNickName=character.streaming_nickname
    )
    chat_data = SCHATDATA()
    chat_data.accountId = str(sessions[ctx.transport].account.id)
    chat_data.characterId = str(sessions[ctx.transport].character.id)
    chat_data.nickname.CopyFrom(nickName)
    chat_data.partyId = str(sessions[ctx.transport].party.id)
    chat_data.chatDataPieceArray.append(chat_piece)

    return chat_data


def get_all_gold(character_id, exclude=[]):
    """Helper that gets all the gold items in the inventory of a user"""
    items = inventory.get_all_items(character_id)
    gold_items = []
    total = 0

    for item, _ in items:
        # skip all the items that are not gold
        if "Id_Item_GoldCoins" not in item.item_id and inventory.get_inv_limit(item.item_id) == 0:
            continue

        if (item, []) in exclude:
            continue

        # we have a item that contains/is gold. Add it to the amount and the item list
        if inventory.get_inv_limit(item.item_id):
            total += item.inv_count
        else:
            total += item.quantity

        gold_items.append(item)

    return total, gold_items


def has_gold_amount(character_id, amount, exclude=[]):
    """Helper to check if a the user has at least amount of gold"""
    total, _ = get_all_gold(character_id, exclude)

    return total >= amount


def deduct_gold(character_id, deduct_amount):
    """Helper function to deduct gold from the user"""
    total, items = get_all_gold(character_id)

    # check if we have enough gold
    if total < deduct_amount:
        return False

    # remove the gold from the inventory
    for item in items:
        # get the amount of gold the item has
        count = item.inv_count if inventory.get_inv_limit(item.item_id) else item.quantity

        # get the amount we should remove from this item
        quantity = min(count, deduct_amount)
        deduct_amount -= quantity

        if not inventory.get_inv_limit(item.item_id):
            # we have a stack. Remove the quantity from the item
            item.quantity -= quantity

            # if we have a stack check if we still have something in the stack. Otherwise remove the item
            if item.quantity == 0:
                inventory.delete_item(character_id, item, True)

        else:
            item.inv_count -= quantity

        # check if we have removed enough gold
        if deduct_amount <= 0:
            break

    return True


def get_empty_slot(character_id, size=(1, 1)):
    """Helper function get a empty slot in the inventory"""
    # get the items from the bag and sort them
    items = inventory.get_all_items(character_id, Define_Item.InventoryId.BAG)
    items.sort(key=lambda i: i[0].slot_id, reverse=True)
    items.extend([(None, None)] * (50 - len(items)))

    for index, (item, _) in enumerate(items):
        # TODO: get the size of the current item and use the size of the item we want to place
        if item is None or index != item.slot_id:
            return (Define_Item.InventoryId.BAG, index + 1)

    # do the same thing for the storage
    items = inventory.get_all_items(character_id, Define_Item.InventoryId.STORAGE)
    items.sort(key=lambda i: i[0].slot_id, reverse=True)
    items.extend([(None, None)] * (240 - len(items)))

    for index, (item, _) in enumerate(items):
        # TODO: get the size of the current item and use the size of the item we want to place
        if item is None or index != item.slot_id:
            return (Define_Item.InventoryId.STORAGE, index)

    # we have no space return None
    return (None, None)


def get_trade_reqs(ctx, msg):
    """Occurs when the user is not a trader and opens the trade screen"""
    return SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES(
        requirements=[
            STRADE_MEMBERSHIP_REQUIREMENT(
                memberShipType=Define_Trade.Requirement_Type.MINIMUM_LEVEL, memberShipValue=5
            ),
            STRADE_MEMBERSHIP_REQUIREMENT(
                memberShipType=Define_Trade.Requirement_Type.INITIATION_FEE, memberShipValue=initial_trade_fee
            ),
            STRADE_MEMBERSHIP_REQUIREMENT(
                memberShipType=Define_Trade.Requirement_Type.COST_PER_TRADE, memberShipValue=trade_fee
            ),
        ]
    )


def get_channels(ctx, msg):
    """Occurs when the user is a trader and opens the trader screen"""
    res = SS2C_TRADE_CHANNEL_LIST_RES()
    res.isTrader = sessions[ctx.transport].character.is_trader

    # add all the available channels
    for ch in channels:
        res.channels.append(
            STRADE_CHANNEL(
                index=ch["index"],
                channelName="ChatRoomData:Id_ChatRoom_Trade_" + ch["name"],
                memberCount=len(ch["clients"]),
                roomType=1,  # TODO: change this to a room type (Define_Chat.RoomType)
                groupIndex=1,
            )
        )

    return res


def select_channel(ctx, msg):
    """Occurs when the user selects a trading channel"""
    req = SC2S_TRADE_CHANNEL_SELECT_REQ()
    req.ParseFromString(msg)

    # check if we have a valid channel
    if req.index == 0 or req.index > len(channels):
        return SS2C_TRADE_CHANNEL_SELECT_RES(result=pc.FAIL_TRADE_REQUEST_NOT_FOUND_CHANNEL)

    # do not update anything if we already have the client in the channel list (for some reason it sometimes
    # sends this message 2x)
    if ctx in channels[req.index - 1]["clients"]:
        return SS2C_TRADE_CHANNEL_SELECT_RES(result=pc.SUCCESS)

    # send a notification to all the players in the channel
    char = sessions[ctx.transport].character
    for client in channels[req.index - 1]["clients"]:
        client.reply(
            SS2C_TRADE_CHANNEL_USER_UPDATE_NOT(
                updates=[
                    STRADE_CHANNEL_USER_UPDATE_INFO(
                        trader=get_trader_info(char, str(sessions[ctx.transport].account.id)),
                        updateFlag=Define_Message.UpdateFlag.INSERT,
                    )
                ]
            )
        )

    # send all the current users to the new player
    notify = SS2C_TRADE_CHANNEL_USER_UPDATE_NOT()
    for client in channels[req.index - 1]["clients"]:
        char = sessions[client.transport].character

        trader = STRADE_CHANNEL_USER_UPDATE_INFO(
            trader=get_trader_info(char, str(sessions[client.transport].account.id)),
            updateFlag=Define_Message.UpdateFlag.INSERT,
        )
        notify.updates.append(trader)

    ctx.reply(notify)

    # add the user to the channel list
    channels[req.index - 1]["clients"].append(ctx)
    return SS2C_TRADE_CHANNEL_SELECT_RES(result=pc.SUCCESS)


def exit_channel(ctx, msg):
    """Occurs when the player exits a channel"""
    # find the client's channel
    channel = get_current_channel(ctx)

    if not channel:
        # return a success anyway. Do not block a exit
        return SS2C_TRADE_CHANNEL_EXIT_RES(result=pc.SUCCESS)

    # leave the channel
    leave_channel(ctx, channel)

    # send a delete for every character to the character that is leaving
    notify = SS2C_TRADE_CHANNEL_USER_UPDATE_NOT()
    for client in channel["clients"]:
        char = sessions[client.transport].character

        trader = STRADE_CHANNEL_USER_UPDATE_INFO(
            trader=get_trader_info(char, str(sessions[client.transport].account.id)),
            updateFlag=Define_Message.UpdateFlag.DELETE,
        )
        notify.updates.append(trader)

    ctx.reply(notify)

    return SS2C_TRADE_CHANNEL_EXIT_RES(result=pc.SUCCESS)


def trade_request(ctx, msg):
    """Occurs when a trade request is send by a user"""
    req = SC2S_TRADE_REQUEST_REQ()
    req.ParseFromString(msg)

    # check if we have enough gold
    if not has_gold_amount(sessions[ctx.transport].character.id, trade_fee):
        return SS2C_TRADE_REQUEST_RES(result=pc.FAIL_TRADE_REQUIREMENT_SHORTAGE_GOLD)

    # get the channel we are in
    channel = get_current_channel(ctx)

    if channel is None:
        return SS2C_TRADE_REQUEST_RES(result=pc.FAIL_GENERAL)

    # find the other user in the current channel
    other = get_user_in_channel(channel, req.accountId)

    if other is None:
        return SS2C_TRADE_REQUEST_RES(result=pc.FAIL_GENERAL)

    # check if the other has enough gold
    if not has_gold_amount(sessions[other.transport].character.id, trade_fee):
        return SS2C_TRADE_REQUEST_RES(result=pc.FAIL_TRADE_REQUIREMENT_SHORTAGE_GOLD)

    # send a trade notification to the player
    notify = SS2C_TRADE_REQUEST_NOT()
    notify.accountId = str(sessions[ctx.transport].account.id)
    notify.nickName.CopyFrom(req.nickName)
    other.reply(notify)

    return SS2C_TRADE_REQUEST_RES(result=pc.SUCCESS, requestNickName=req.nickName)


def cancel_trade(ctx, msg):
    """Occurs when the user cancels a trade"""
    # get the other player to send a stop message
    trade, _, other = find_trade(ctx)

    if trade and other:
        other.ctx.reply(SS2C_TRADING_CLOSE_RES(result=pc.SUCCESS))

    # remove the trade
    trades.remove(trade)

    return SS2C_TRADING_CLOSE_RES(result=pc.SUCCESS)


def ready(ctx, msg):
    """Occurs when a user presses ready on the first trader menu"""
    req = SC2S_TRADING_READY_REQ()
    req.ParseFromString(msg)

    # get all the parties in the trade
    trade, current, other = find_trade(ctx)

    if not all([trade, current, other]):
        return SS2C_TRADING_READY_RES(result=pc.FAIL_GENERAL)

    # check if we have enough gold in our inventory
    if req.isReady and not has_gold_amount(sessions[ctx.transport].character.id, trade_fee, current.inventory):
        return SS2C_TRADING_READY_RES(result=pc.FAIL_TRADING_READY_SHORTAGE_GOLD)

    # send the ready change to all the parties
    for client in [current, other]:
        notify = SS2C_TRADING_READY_NOT()
        notify.readyUserInfo.CopyFrom(get_trading_info(ctx))
        notify.isReady = req.isReady

        client.ctx.reply(notify)

    # update the internal state of the trade
    current.is_ready = req.isReady

    # check if we need to send the confirm message
    if current.is_ready and other.is_ready:
        # clear the is ready flags to reuse them for the confirm message
        current.is_ready = False
        other.is_ready = False

        # TODO: add the correct items in the packet. For some reason the game accepts it without any
        # issue if it doesnt have it.
        notify = SS2C_TRADING_CONFIRM_NOT()
        # notify.target =
        # notify.mine =

        # send the confirm message to all parties
        for client in [current, other]:
            client.ctx.reply(notify)

    return SS2C_TRADING_READY_RES(result=pc.SUCCESS)


def confirm(ctx, msg):
    """Occurs when a user presses confirm on the second trader menu"""
    req = SC2S_TRADING_CONFIRM_READY_REQ()
    req.ParseFromString(msg)

    # get all the parties in the trade
    trade, current, other = find_trade(ctx)

    if not all([trade, current, other]):
        return SS2C_TRADING_READY_RES(result=pc.FAIL_GENERAL)

    # send the ready change to all the parties
    for client in [current, other]:
        notify = SS2C_TRADING_CONFIRM_READY_NOT()
        notify.readyUserInfo.CopyFrom(get_trading_info(ctx))
        notify.isReady = req.isReady

        client.ctx.reply(notify)

    # update the internal state of the trade
    current.is_ready = req.isReady
    ctx.reply(SS2C_TRADING_CONFIRM_READY_RES(result=pc.SUCCESS))

    # check if we need to send the confirm message
    if current.is_ready and other.is_ready:
        notify = SS2C_TRADING_RESULT_NOT()
        notify.result = pc.SUCCESS

        # remove the gold from the inventory of both parties
        for client in [current, other]:
            deduct_gold(sessions[client.ctx.transport].character.id, trade_fee)

        # send the confirm message to all parties
        for client in [current, other]:
            client.ctx.reply(notify)

        # TODO: This should be done proper
        # change the owner of the items and move the item to a empty location
        for item in current.inventory:
            inventory_id, slot_id = get_empty_slot(sessions[other.ctx.transport].character.id)

            item[0].character_id = sessions[other.ctx.transport].character.id
            item[0].location_id = inventory_id
            item[0].slot_id = slot_id
        for item in other.inventory:
            inventory_id, slot_id = get_empty_slot(sessions[other.ctx.transport].character.id)

            item[0].character_id = sessions[current.ctx.transport].character.id
            item[0].location_id = inventory_id
            item[0].slot_id = slot_id

        # update the items on both sides
        for client in [current, other]:
            client.ctx.reply(HCharacter.character_info(client.ctx, bytearray()))

        # exit the trade after we have updated everything
        for client in [current, other]:
            client.ctx.reply(SS2C_TRADING_CLOSE_RES(result=pc.SUCCESS))

        # remove the trade from the trade list
        trades.remove(trade)

    return None


def cancel_confirm(ctx, msg):
    """Occurs when a user cancels a trade in the confirm stage"""
    # get the current trade
    _, current, other = find_trade(ctx)

    # send the cancel to the other party
    if other:
        other.ctx.reply(SS2C_TRADING_CONFIRM_CANCEL_RES(result=pc.SUCCESS))

    # clear the ready state of both parties
    current.is_ready = False
    other.is_ready = False

    return SS2C_TRADING_CONFIRM_CANCEL_RES(result=pc.SUCCESS)


def accept_invite(ctx, msg):
    """Occurs when the user accepts/refuses a trading invite"""
    req = SC2S_TRADE_ANSWER_REQ()
    req.ParseFromString(msg)

    # get the channel we are in
    channel = get_current_channel(ctx)

    if channel is None:
        return SS2C_TRADE_REQUEST_RES(result=pc.FAIL_GENERAL)

    # find the player the request came from
    other = get_user_in_channel(channel, req.accountId)

    if other is None:
        return SS2C_TRADE_ANSWER_RES(result=pc.FAIL_GENERAL)

    # send the notification to the other player
    if req.selectFlag != Define_Message.SelectFlag.OK:
        notify = SS2C_TRADE_ANSWER_REFUSAL_NOT()
        notify.accountId = str(sessions[ctx.transport].account.id)
        notify.nickName.CopyFrom(req.nickName)

        other.reply(notify)
    else:
        # add the users to the trading dictionary
        trade = Trade(TradeParty(ctx), TradeParty(other))
        trades.append(trade)

        # get the other party
        target_info = STRADING_USER_INFO()
        target_info.nickName.CopyFrom(req.nickName)
        target_info.accountId = req.accountId

        # create the notification
        notify = SS2C_TRADING_BEGIN_NOT()
        notify.target.CopyFrom(target_info)
        notify.mine.CopyFrom(get_trading_info(ctx))
        notify.tradeFee = trade_fee

        # TODO: get the actual reset time
        notify.moveResetTimeSec = 3

        # send the notification to all the players
        for client in [ctx, other]:
            client.reply(notify)

    return SS2C_TRADE_ANSWER_RES(result=pc.SUCCESS)


def move_item(ctx, msg):
    """Occurs when the user moves items in/out of the trading inventory"""
    req = SC2S_TRADING_ITEM_UPDATE_REQ()
    req.ParseFromString(msg)

    # get the other client
    _, current, other = find_trade(ctx)

    if other is None:
        return SS2C_TRADING_ITEM_UPDATE_RES(result=pc.FAIL_GENERAL)

    char = sessions[ctx.transport].character

    # get the item at the location
    item = db.query(Item).filter_by(character_id=char.id).filter_by(id=req.uniqueId).first()

    if item is None:
        return SS2C_TRADING_ITEM_UPDATE_RES(result=pc.FAIL_GENERAL)

    attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()

    # update the trade inventory with the item
    if req.updateFlag == Define_Message.UpdateFlag.INSERT:
        current.inventory.append((item, attributes))
    elif req.updateFlag == Define_Message.UpdateFlag.DELETE:
        current.inventory.remove((item, attributes))

        # clear the states of all users and send a notification
        current.is_ready = False
        other.is_ready = False

        # send the ready change to all the parties
        for client in [current, other]:
            notify = SS2C_TRADING_READY_NOT()
            notify.readyUserInfo.CopyFrom(get_trading_info(client.ctx))
            notify.isReady = client.is_ready

            for client in [current, other]:
                client.ctx.reply(notify)

    # create the proto item with the correct slot id
    pItem = HCharacter.item_to_proto_item(item, attributes)
    pItem.slotId = req.slotId

    res = SS2C_TRADING_ITEM_UPDATE_RES()
    res.result = pc.SUCCESS
    res.updateUserInfo.CopyFrom(get_trading_info(ctx))
    res.updateFlag = req.updateFlag
    res.updateItem.CopyFrom(pItem)

    # send the response to the other client
    other.ctx.reply(res)

    # send the response to the client
    return res


def private_chat(ctx, msg):
    """Occurs when the user sends a message in the trading chat"""
    req = SC2S_TRADING_CHAT_REQ()
    req.ParseFromString(msg)

    # search for the current trade we are doing
    trade, _, other = find_trade(ctx)

    chat_trade = STRADE_CHAT_S2C()
    chat_trade.index = trade.id
    chat_trade.chatType = req.chat.chatType
    chat_trade.time = int(arrow.utcnow().timestamp())
    chat_trade.chatData.CopyFrom(create_chat_data(ctx, req))

    # check if we found it
    if all([trade, other]):
        # send the message to the other party
        other.ctx.reply(SS2C_TRADING_CHAT_RES(result=pc.SUCCESS, chat=chat_trade))

    return None


def chat(ctx, msg):
    """Occurs when a user sends a message in the channel chat"""
    req = SC2S_TRADE_CHANNEL_CHAT_REQ()
    req.ParseFromString(msg)

    chat_trade = STRADE_CHAT_S2C()
    chat_trade.index = 1
    chat_trade.chatType = req.chat.chatType
    chat_trade.time = int(arrow.utcnow().timestamp())
    chat_trade.chatData.CopyFrom(create_chat_data(ctx, req))

    # Broadcast the message to other clients
    broadcast_chat(ctx, [chat_trade])

    return SS2C_TRADE_CHANNEL_CHAT_RES(result=pc.SUCCESS, chats=[chat_trade])


def process_membership(ctx, msg):
    """Occurs when the user tries to become a trader"""
    char = sessions[ctx.transport].character

    # check if the level of the user is high enough
    if char.level < 5:
        return SS2C_TRADE_MEMBERSHIP_RES(result=pc.FAIL_TRADE_REQUIREMENT_SHORTAGE_LV)

    # check if the user is a trader already
    if char.is_trader:
        return SS2C_TRADE_MEMBERSHIP_RES(result=pc.FAIL_TRADE_ALREADY_MEMBERSHIP)

    # Try to deduct the gold. Send a error if the user does not have enough gold
    if not deduct_gold(char.id, initial_trade_fee):
        return SS2C_TRADE_MEMBERSHIP_RES(result=pc.FAIL_TRADE_REQUIREMENT_SHORTAGE_GOLD)

    # the user has become a trader. Update in the database
    sessions[ctx.transport].character.is_trader = True

    # send the return state
    ctx.reply(SS2C_TRADE_MEMBERSHIP_RES(result=pc.SUCCESS))

    # update the player inventory
    return HCharacter.character_info(ctx, bytearray())
