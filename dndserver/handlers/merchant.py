import arrow
import re

from dndserver.database import db
from dndserver.data import merchant as MerchantData
from dndserver.enums.classes import MerchantClass
from dndserver.models import Merchant, MerchantItem, MerchantItemAttribute, ItemAttribute, Item
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
)
from dndserver.handlers import character, inventory


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

    return ret


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


def db_create_merchant_item(merchant_id, item, index, remaining):
    """Creates a database entry for the merchant with item attributes and the amount remaining"""
    it = MerchantItem()
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
        attr = MerchantItemAttribute()
        attr.item_id = it.id
        attr.primary = True
        attr.property = attribute.propertyTypeId
        attr.value = attribute.propertyValue

        attr.save()

    for attribute in item.secondaryPropertyArray:
        attr = MerchantItemAttribute()
        attr.item_id = it.id
        attr.primary = False
        attr.property = attribute.propertyTypeId
        attr.value = attribute.propertyValue

        attr.save()


def generate_items_merchant(character_id, merchant_id, remaining):
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

    for index, item in enumerate(items):
        # create the default items for every merchant
        db_create_merchant_item(merchant_id, item, index + 1, remaining)


def add_to_inventory_merchant(trade_id, info, character_id):
    """Helper function to add a bought item to the inventory of the character"""
    # get the item from the database. Get the unique id is always 0. Check what item we
    # got by getting the merchant id and the index from the trade id
    index = int(re.sub("\\D", "", trade_id))
    re_merchant = re.search(".*Id_StockBuy_(.*?)_.*", trade_id)

    # make sure we have a valid regex
    if re_merchant is None:
        return False

    # get the merchant from the name
    merchant = (
        db.query(Merchant)
        .filter_by(
            character_id=character_id, merchant=MerchantClass("DesignDataMerchant:Id_Merchant_" + re_merchant.group(1))
        )
        .first()
    )

    if merchant is None:
        return False

    # get the selected item
    item = db.query(MerchantItem).filter_by(merchant_id=merchant.id).filter_by(index=index).first()

    # check if we have the item
    if item is None or item.remaining == 0:
        return False

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
    attributes = db.query(MerchantItemAttribute).filter_by(item_id=item.id).all()
    for attribute in attributes:
        attr = ItemAttribute()
        attr.item_id = it.id
        attr.primary = attribute.primary
        attr.property = attribute.property
        attr.value = attribute.value

        attr.save()

    # remove 1 item from the item we bought
    item.remaining -= 1

    return True


def get_merchant_list(ctx, msg):
    """Occurs when the user opens the merchant menu"""
    # get all the times for every merchant
    merchants = db.query(Merchant).filter_by(character_id=sessions[ctx.transport].character.id).all()

    # return all the merchants we have
    res = SS2C_MERCHANT_LIST_RES()

    # add every merchant we have available for this character
    for merchant in merchants:
        # check if the timer has passed
        if arrow.utcnow() >= merchant.refresh_time:
            # timer has passed. Delete all the items for the merchant to signal the get list
            # to spawn new items when requested
            items = db.query(MerchantItem).filter_by(merchant_id=merchant.id).all()

            for item in items:
                # get the attributes for the item
                attributes = db.query(MerchantItemAttribute).filter_by(item_id=item.id).all()

                for attribute in attributes:
                    attribute.delete()

                item.delete()

            # update the time
            merchant.refresh_time = arrow.utcnow().shift(minutes=15)

        # append the merchant to the list with the time
        res.merchantList.append(
            SMERCHANT_INFO(
                merchantId=MerchantClass(merchant.merchant).value,
                faction=0,
                remainTime=(merchant.refresh_time - arrow.utcnow()).seconds,
                isUnidentified=1,
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

    # search for the trader we have selected
    merchant = (
        db.query(Merchant)
        .filter_by(character_id=sessions[ctx.transport].character.id, merchant=MerchantClass(req.merchantId))
        .first()
    )

    # get all the item this merchant is selling
    items = db.query(MerchantItem).filter_by(merchant_id=merchant.id).all()

    # check if we have any items to show. If we dont we regenerate them
    if len(items) == 0:
        # TODO: unhardcode this
        items_remaining = 3

        # we have no items regenerate them
        generate_items_merchant(sessions[ctx.transport].character.id, merchant.id, items_remaining)

        # requery the items to fetch all the new items
        items = db.query(MerchantItem).filter_by(merchant_id=merchant.id).all()

    res = SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES()
    res.result = pc.SUCCESS
    res.loopMessageFlag = Define_Message.LoopFlag.PROGRESS

    for item in items:
        # skip items we dont have anything left of
        if item.remaining == 0:
            continue

        # get the attributes for the item
        attributes = db.query(MerchantItemAttribute).filter_by(item_id=item.id).all()

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

        # remove the provided quantity from the user
        if (query.quantity - item.itemCount) <= 0:
            # delete the item from the database
            inventory.delete_item(sessions[ctx.transport].character.id, item)
        else:
            query.quantity -= item.itemCount

    # add the new items to the inventory
    for info in req.merchantSlotInfo:
        add_to_inventory_merchant(req.tradeId, info, sessions[ctx.transport].character.id)

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
