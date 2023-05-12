from dndserver.data import merchant as Merchant
from dndserver.objects import items
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Defines import Define_Message
from dndserver.enums.items import ItemType, Rarity, Item
from dndserver.models import Item as mItem
from dndserver.handlers import character, inventory
from dndserver.persistent import sessions
from dndserver.protos.Merchant import (
    SC2S_MERCHANT_STOCK_BUY_ITEM_LIST_REQ,
    SC2S_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_REQ,
    SMERCHANT_INFO,
    SMERCHANT_STOCK_BUY_ITEM_INFO,
    SMERCHANT_STOCK_SELL_BACK_ITEM_INFO,
    SS2C_MERCHANT_LIST_RES,
    SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES,
    SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES,
    SC2S_MERCHANT_STOCK_SELL_BACK_REQ,
    SS2C_MERCHANT_STOCK_SELL_BACK_RES
)
from dndserver.protos.Inventory import SS2C_INVENTORY_SINGLE_UPDATE_RES


def create_merchant(name, remaining_time):
    """Helper function to create a merchant"""
    return SMERCHANT_INFO(merchantId=name, faction=0, remainTime=remaining_time, isUnidentified=0)


def get_merchant_list(ctx, msg):
    """Occurs when the user opens the merchant menu"""
    # TODO: update make the timers update. In the data the faction and
    # isUnidentified is zero for all merchants. Check if this is correct
    # as well
    remaining_time = 10000

    # return all the merchants we have
    return SS2C_MERCHANT_LIST_RES(
        merchantList=[
            create_merchant("DesignDataMerchant:Id_Merchant_Surgeon", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Santa", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Woodsman", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Tailor", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Treasurer", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Leathersmith", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Armourer", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_TheCollector", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Alchemist", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_TavernMaster", remaining_time),
            create_merchant("DesignDataMerchant:Id_Merchant_Weaponsmith", remaining_time),
        ]
    )


def get_buy_list(ctx, msg):
    """Occurs when the user opens one of the merchant menus"""
    # To list the stock we need to send 3 messages.
    # 1 for starting, 1 with the actual data and the last for the end
    req = SC2S_MERCHANT_STOCK_BUY_ITEM_LIST_REQ()
    req.ParseFromString(msg)

    # TODO: handle every trader differently

    # send stage 1 (start)
    ctx.reply(
        SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(
            result=pc.SUCCESS, loopMessageFlag=Define_Message.LoopFlag.BEGIN, stockList=[]
        )
    )

    # send stage 2 (data the merchant is selling)
    ctx.reply(
        SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(
            result=pc.SUCCESS,
            loopMessageFlag=Define_Message.LoopFlag.PROGRESS,
            stockList=[
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_01",
                    stockUniqueId=1,
                    itemInfo=items.generate_item(Item.BANDAGE, ItemType.CONSUMABLES, Rarity.JUNK, 3, 14, 1, 1111111),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_02",
                    stockUniqueId=2,
                    itemInfo=items.generate_item(Item.TORCH, ItemType.WEAPONS, Rarity.JUNK, 3, 13, 1, 1111112),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_03",
                    stockUniqueId=3,
                    itemInfo=items.generate_item(Item.ROUNDSHIELD, ItemType.WEAPONS, Rarity.JUNK, 3, 11, 1, 1111113),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_04",
                    stockUniqueId=4,
                    itemInfo=items.generate_item(Item.LANTERN, ItemType.UTILITY, Rarity.JUNK, 3, 8, 1, 1111114),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_05",
                    stockUniqueId=5,
                    itemInfo=items.generate_item(Item.ARMINGSWORD, ItemType.WEAPONS, Rarity.JUNK, 3, 10, 1, 1111115),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_06",
                    stockUniqueId=6,
                    itemInfo=items.generate_item(Item.CLOTHPANTS, ItemType.ARMORS, Rarity.JUNK, 3, 4, 1, 1111116),
                ),
            ],
        )
    )

    # let the protocol send stage 3
    return SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(
        result=pc.SUCCESS, loopMessageFlag=Define_Message.LoopFlag.END, stockList=[]
    )


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
    for merchant, item_store_ids in zip(Merchant.sellback.keys(), Merchant.sellback.values()):
        for id in item_store_ids:
            sellback.stockList.append(SMERCHANT_STOCK_SELL_BACK_ITEM_INFO(stockSellBackId=merchant, stockUniqueId=id))

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

    for sellBackInfo in req.sellBackInfos:
        inventory.delete_item(cid, sellBackInfo) # delete the items that you are selling

    for recievedInfo in req.receivedInfos:
        # selling an item should only ever return gold coins, with the exception of starter gear which doesn't return a recievedInfo
        if recievedInfo.itemId != "DesignDataItem:Id_Item_GoldCoins": return

        # generate item data using the recievedInfo
        item_generated = items.generate_item(
            Item.GOLDCOINS,
            ItemType.LOOTABLES,
            Rarity.NONE,
            recievedInfo.inventoryId,
            recievedInfo.slotId,
            recievedInfo.itemCount)

        # and then add it to the inventory
        item_real = mItem()
        item_real.character_id = cid
        item_real.item_id = item_generated.itemId
        item_real.quantity = item_generated.itemCount
        item_real.inventory_id = item_generated.inventoryId
        item_real.slot_id = item_generated.slotId
        item_real.save()
    
    ctx.reply(SS2C_MERCHANT_STOCK_SELL_BACK_RES(result=pc.SUCCESS))
    # send the character info after selling an item, updates the inventory
    return character.character_info(ctx=ctx, msg=bytearray())