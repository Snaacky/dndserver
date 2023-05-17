import arrow

from dndserver.database import db
from dndserver.data import merchant as MerchantData
from dndserver.enums.classes import MerchantClass
from dndserver.models import Merchant, ItemAttribute, Item
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Defines import Define_Message
from dndserver.enums.items import ItemType, Rarity
from dndserver.enums.items import Item as eItem
from dndserver.objects import items as ObjItems
from dndserver.protos.Merchant import (
    SC2S_MERCHANT_STOCK_BUY_ITEM_LIST_REQ,
    SC2S_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_REQ,
    SMERCHANT_INFO,
    SMERCHANT_STOCK_BUY_ITEM_INFO,
    SMERCHANT_STOCK_SELL_BACK_ITEM_INFO,
    SS2C_MERCHANT_LIST_RES,
    SC2S_MERCHANT_STOCK_BUY_REQ,
    SS2C_MERCHANT_STOCK_BUY_RES,
    SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES,
    SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES,
    SC2S_MERCHANT_STOCK_SELL_BACK_REQ,
    SS2C_MERCHANT_STOCK_SELL_BACK_RES,
)
from dndserver.handlers import character, inventory


def delete_items_merchant(merchant_id):
    """Helper function to delete all items a merchant has"""
    items = db.query(Item).filter_by(merchant_id=merchant_id).all()

    for item in items:
        # get the attributes for the item
        attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()

        for attribute in attributes:
            attribute.delete()

        item.delete()


def delete_merchants(character_id):
    """Helper function to delete all merchants and items they have"""
    merchants = db.query(Merchant).filter_by(character_id=character_id).all()

    for merchant in merchants:
        # delete all the items with attributes
        delete_items_merchant(merchant.id)

        # delete the merchant
        merchant.delete()


def create_merchants(character_id):
    """Helper function to create merchants for a character"""
    # create all the merchants for the user
    for merchant in MerchantClass:
        # create the merchant. Set the refresh to 15 minutes
        db_create_merchant(character_id, merchant, arrow.utcnow().shift(minutes=15))


def get_stockbuy_id(merchant, index):
    """Helper to create the string for the stockbuy id"""
    ret = "DesignDataStockBuy:Id_StockBuy_"

    if merchant == MerchantClass.SURGEON:
        ret += "Surgeon"
    elif merchant == MerchantClass.SANTA:
        ret += "Santa"
    elif merchant == MerchantClass.WOODSMAN:
        ret += "Woodsman"
    elif merchant == MerchantClass.TAILOR:
        ret += "Tailor"
    elif merchant == MerchantClass.TREASURER:
        ret += "Treasurer"
    elif merchant == MerchantClass.LEATHERSMITH:
        ret += "Leathersmith"
    elif merchant == MerchantClass.ARMOURER:
        ret += "Armourer"
    elif merchant == MerchantClass.THECOLLECTOR:
        ret += "Pickaxe"
    elif merchant == MerchantClass.ALCHEMIST:
        ret += "Alchemist"
    elif merchant == MerchantClass.TAVERNMASTER:
        ret += "TavernMaster"
    elif merchant == MerchantClass.WEAPONSMITH:
        ret += "Weaponsmith"
    elif merchant == MerchantClass.GOBLINMERCHANT:
        ret += "GoblinMerchant"
    elif merchant == MerchantClass.VALENTINE:
        ret += "Valentine"
    elif merchant == MerchantClass.PUMPKINMAN:
        ret += "PumpkinMan"

    return ret + "_{0:0>2}".format(index)


def get_stock_unique_id(merchant, index):
    """Helper function to get the stock unique id for the merchant and index"""
    # TODO: use the mapping for the stock unique id. For now use the index
    return index


def db_create_merchant(character_id, merchant_class, refresh_time):
    """Helper function to create a merchant in the database"""
    merchant = Merchant()
    merchant.character_id = character_id
    merchant.merchant = merchant_class
    merchant.refresh_time = refresh_time

    merchant.save()


def db_create_merchant_item(merchant_id, item, index, remaining, character_id):
    """Creates a database entry for the merchant with item attributes and the amount remaining"""
    it = Item()
    it.character_id = character_id
    it.merchant_id = merchant_id
    it.remaining = remaining
    it.index = index

    it.item_id = item.itemId
    it.quantity = item.itemCount
    it.quantity = item.itemCount
    it.ammo_count = item.itemAmmoCount
    it.inv_count = item.itemContentsCount

    it.save()

    # add the attributes to the items
    for attribute in item.primaryPropertyArray:
        attr = ItemAttribute()
        attr.item_id = it.id
        attr.primary = True
        attr.property = attribute.propertyTypeId
        attr.value = attribute.propertyValue

        attr.save()

    for attribute in item.secondaryPropertyArray:
        attr = ItemAttribute()
        attr.item_id = it.id
        attr.primary = False
        attr.property = attribute.propertyTypeId
        attr.value = attribute.propertyValue

        attr.save()


def generate_items_merchant(merchant, merchant_id, remaining, character_id):
    """Helper to generate items for a merchant"""
    # TODO: this should generate items specific for the merchant
    items = [
        ObjItems.generate_item(eItem.BANDAGE, ItemType.CONSUMABLES, Rarity.JUNK, 3, 14, 1, 1111111),
        ObjItems.generate_item(eItem.TORCH, ItemType.WEAPONS, Rarity.JUNK, 3, 13, 1, 1111112),
        ObjItems.generate_item(eItem.ROUNDSHIELD, ItemType.WEAPONS, Rarity.JUNK, 3, 11, 1, 1111113),
        ObjItems.generate_item(eItem.LANTERN, ItemType.UTILITY, Rarity.JUNK, 3, 8, 1, 1111114),
        ObjItems.generate_item(eItem.ARMINGSWORD, ItemType.WEAPONS, Rarity.JUNK, 3, 10, 1, 1111115),
        ObjItems.generate_item(eItem.CLOTHPANTS, ItemType.ARMORS, Rarity.JUNK, 3, 4, 1, 1111116),
    ]

    # get the stock index map for the current merchant (never add 2 items within the
    # same index in the map. The game will only return 1 index)
    merchant_map = MerchantData.buy_mapping[merchant]

    # TODO: every merchant has its own index. Convert the item to a merchant index. Prices
    # are determined by the offet from the start of the merchant stock id. For now we map
    # the index to the first stock id. Prices are determined from the stock id.
    for (index, variations), item in zip(merchant_map, items):
        # create the default items for every merchant
        db_create_merchant_item(merchant_id, item, index, remaining, character_id)


def add_to_inventory_merchant(unique_id, info, character_id):
    """Helper function to add a bought item to the inventory of the character"""
    # get the selected item from the database
    item = db.query(Item).filter_by(character_id=character_id).filter_by(index=unique_id).first()

    # check if we have the item
    if item is None or item.remaining == 0:
        return False

    # check if we need to merge or create a new item
    if info.itemUniqueId == 0:
        # create a new item for the user. Copy the item from the db to the
        it = Item()
        it.item_id = item.item_id
        it.quantity = item.quantity
        it.ammo_count = item.ammo_count
        it.inv_count = item.inv_count

        it.character_id = character_id
        it.inventory_id = info.inventoryId
        it.slot_id = info.slotId

        it.save()

        # get all the attributes the item has
        attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()
        for attribute in attributes:
            attr = ItemAttribute()
            attr.item_id = it.id
            attr.primary = attribute.primary
            attr.property = attribute.property
            attr.value = attribute.value

            attr.save()
    else:
        # we need to merge. Add to the count of the item
        it = db.query(Item).filter_by(id=info.itemUniqueId).first()

        # increment the item with the item count
        it.quantity += item.quantity

    # remove 1 item from the item we bought
    item.remaining -= 1

    return True


def get_merchant_list(ctx, msg):
    """Occurs when the user opens the merchant menu"""
    # get all the times for every merchant
    merchants = db.query(Merchant).filter_by(character_id=sessions[ctx.transport].character.id).all()

    # check if the user has the merchants
    if len(merchants) == 0:
        # add the merchants
        create_merchants(sessions[ctx.transport].character.id)

        # update the query
        merchants = db.query(Merchant).filter_by(character_id=sessions[ctx.transport].character.id).all()

    # return all the merchants we have
    res = SS2C_MERCHANT_LIST_RES()

    # add every merchant we have available for this character
    for merchant in merchants:
        # check if the timer has passed
        if arrow.utcnow() >= merchant.refresh_time:
            # timer has passed. Delete all the items for the merchant to signal the get list
            # to spawn new items when requested
            delete_items_merchant(merchant.id)

            # update the time
            merchant.refresh_time = arrow.utcnow().shift(minutes=15)

        # append the merchant to the list with the time
        res.merchantList.append(
            SMERCHANT_INFO(
                merchantId=MerchantClass(merchant.merchant).value,
                faction=0,
                remainTime=(merchant.refresh_time - arrow.utcnow()).seconds,
                isUnidentified=0,
            ),
        )

    return res


def get_buy_list(ctx, msg):
    """Occurs when the user opens one of the merchant menus"""
    # To list the stock we need to send 3 messages.
    # 1 for starting, 1 with the actual data and the last for the end
    req = SC2S_MERCHANT_STOCK_BUY_ITEM_LIST_REQ()
    req.ParseFromString(msg)

    # send stage 1 (start)
    ctx.reply(
        SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(
            result=pc.SUCCESS, loopMessageFlag=Define_Message.LoopFlag.BEGIN, stockList=[]
        )
    )

    char = sessions[ctx.transport].character

    # search for the trader we have selected
    merchant = db.query(Merchant).filter_by(character_id=char.id, merchant=MerchantClass(req.merchantId)).first()

    # get all the item this merchant is selling
    items = db.query(Item).filter_by(merchant_id=merchant.id).all()

    # check if we have any items to show. If we dont we regenerate them
    if len(items) == 0:
        # TODO: unhardcode this
        items_remaining = 3

        # we have no items regenerate them
        generate_items_merchant(merchant.merchant, merchant.id, items_remaining, char.id)

        # requery the items to fetch all the new items
        items = db.query(Item).filter_by(merchant_id=merchant.id).all()

    res = SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES()
    res.result = pc.SUCCESS
    res.loopMessageFlag = Define_Message.LoopFlag.PROGRESS

    for item in items:
        # skip items we dont have anything left of
        if item.remaining == 0:
            continue

        attributes = []

        # check if we should show the attributes and stats
        if merchant.merchant != MerchantClass.GOBLINMERCHANT:
            # get the attributes for the item
            attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()

        else:
            # we should not show the stats. Replace all the stats for "Unidentified"
            item_attr = db.query(ItemAttribute).filter_by(item_id=item.id).all()

            # make sure we have at least one primary item in the item attributes. Otherwise
            # the game will show random stats
            if not any(attr.primary for attr in item_attr):
                # for some reason the item does not have a primary property. Add the unidentified here
                at = ItemAttribute()
                at.item_id = item.id
                at.primary = True
                at.property = "DesignDataItemPropertyType:Id_ItemPropertyType_Unidentified"
                at.value = True
                attributes.append(at)

            # add all the attributes as hidden
            for attr in item_attr:
                at = ItemAttribute()
                at.item_id = item.id
                at.primary = attr.primary
                at.property = "DesignDataItemPropertyType:Id_ItemPropertyType_Unidentified"
                at.value = True
                attributes.append(at)

        res.stockList.append(
            SMERCHANT_STOCK_BUY_ITEM_INFO(
                stockBuyId=get_stockbuy_id(merchant.merchant, item.index),
                stockUniqueId=get_stock_unique_id(merchant.merchant, item.index),
                itemInfo=character.item_to_proto_item(item, attributes, False),
            )
        )

    # send stage 2 (data the merchant is selling)
    ctx.reply(res)

    # let the protocol send stage 3
    return SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(
        result=pc.SUCCESS, loopMessageFlag=Define_Message.LoopFlag.END, stockList=[]
    )


def buy_item(ctx, msg):
    """Occurs when the user buys a item from the merchant"""
    req = SC2S_MERCHANT_STOCK_BUY_REQ()
    req.ParseFromString(msg)

    # remove the items from the inventory
    for item in req.dealItemList:
        # get the item
        query = (
            db.query(Item)
            .filter_by(character_id=sessions[ctx.transport].character.id)
            .filter_by(id=item.itemUniqueId)
            .first()
        )

        # check if we have the item we want to use to buy the item
        if query is None:
            return SS2C_MERCHANT_STOCK_BUY_RES(result=pc.FAIL_GENERAL)

        # remove the provided quantity from the user. Check where we should remove it
        if item.itemContentsCount:
            # remove from the inventory count
            query.inv_count -= item.itemContentsCount
        elif (query.quantity - item.itemCount) <= 0:
            # delete the item from the database
            inventory.delete_item(sessions[ctx.transport].character.id, item)
        else:
            query.quantity -= item.itemCount

    # add the new items to the inventory
    for info in req.merchantSlotInfo:
        add_to_inventory_merchant(req.stockUniqueId, info, sessions[ctx.transport].character.id)

    # send the final stage
    ctx.reply(SS2C_MERCHANT_STOCK_BUY_RES(result=pc.SUCCESS))

    # send the character info after a trade
    return character.character_info(ctx=ctx, msg=bytearray())


def get_sellback_list(ctx, msg):
    """Occurs when the user opens one of the merchant menus"""
    # To send the items we can sell back to the merchant we need to send 3 messages.
    # 1 for starting, 1 with the actual data and the last for the end
    req = SC2S_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_REQ()
    req.ParseFromString(msg)

    # send stage 1 (start)
    ctx.reply(
        SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES(
            result=pc.SUCCESS, loopMessageFlag=Define_Message.LoopFlag.BEGIN, stockList=[]
        )
    )

    sellback = SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES(
        result=pc.SUCCESS, loopMessageFlag=Define_Message.LoopFlag.PROGRESS
    )

    # TODO: it looks like the game sends every item for every trader in this request (around 1200 items). It will do
    # this every time we change trader. Not sure if this is intended or not. For example in the data of the Alchemist
    # merchant it also sends the sellbacks for the weaponsmith.
    for merchant, item_store_ids in zip(MerchantData.sellback.keys(), MerchantData.sellback.values()):
        for id in item_store_ids:
            sellback.stockList.append(
                SMERCHANT_STOCK_SELL_BACK_ITEM_INFO(stockSellBackId=merchant.value, stockUniqueId=id)
            )

    # send stage 2 (data the merchant is selling)
    ctx.reply(sellback)

    # let the protocol send stage 3
    return SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES(
        result=pc.SUCCESS, loopMessageFlag=Define_Message.LoopFlag.END, stockList=[]
    )


def sellback_request(ctx, msg):
    """Occurs when the user requests to sellback to one of the merchants."""
    req = SC2S_MERCHANT_STOCK_SELL_BACK_REQ()
    req.ParseFromString(msg)
    cid = sessions[ctx.transport].character.id
    # grab all items to sell, then delete them
    for sellBackInfo in req.sellBackInfos:
        inventory.delete_item(cid, sellBackInfo)
    for recievedInfo in req.receivedInfos:
        inventory_item = inventory.get_all_items(
            cid, inventory_id=recievedInfo.inventoryId, slot_id=recievedInfo.slotId
        )
        # if there is an inventory item, we are trying to merge
        if len(inventory_item) != 0:
            # [(<dndserver.models.Item object at 0x000001B1D8DEB040>, [])]
            inventory_item = inventory_item[0][0]
            # if the we're modifying GoldCoins, increase the stack count.
            if recievedInfo.itemId == "DesignDataItem:Id_Item_GoldCoins":
                inventory_item.quantity = inventory_item.quantity + recievedInfo.itemCount
            # otherwise, it's a container, increase the inventory count.
            else:
                inventory_item.inv_count = inventory_item.inv_count + recievedInfo.itemContentsCount
        # now we've processed the stack merging, if there is any requests left to process:
        else:
            # generate item data for that request
            item_generated = ObjItems.generate_item(
                eItem.GOLDCOINS,
                ItemType.LOOTABLES,
                Rarity.NONE,
                recievedInfo.inventoryId,
                recievedInfo.slotId,
                recievedInfo.itemCount,
            )
            # and add it to the player inventory
            item_real = Item()
            item_real.character_id = cid
            item_real.item_id = item_generated.itemId
            item_real.quantity = item_generated.itemCount
            item_real.inventory_id = item_generated.inventoryId
            item_real.slot_id = item_generated.slotId
            item_real.save()
    # we finished selling to the merchant and now we should
    ctx.reply(SS2C_MERCHANT_STOCK_SELL_BACK_RES(result=pc.SUCCESS))
    # send the character info afterwards, updating the inventory
    return character.character_info(ctx=ctx, msg=bytearray())
