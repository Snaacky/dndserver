from dndserver.objects import items
from dndserver.protos.Merchant import (
    SS2C_MERCHANT_LIST_RES,
    SMERCHANT_INFO,
    SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES,
    SMERCHANT_STOCK_BUY_ITEM_INFO,
    SC2S_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_REQ,
    SC2S_MERCHANT_STOCK_BUY_ITEM_LIST_REQ,
    SMERCHANT_STOCK_SELL_BACK_ITEM_INFO,
    SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES,
)


def get_merchant_list(ctx, msg):
    # TODO: update make the timers update. In the data the faction and
    # isUnidentified is zero for all merchants. Check if this is correct
    # as well
    remaining_time = 10000

    # return all the merchants we have
    return SS2C_MERCHANT_LIST_RES(
        merchantList=[
            create_surgeon(remaining_time),
            create_santa(remaining_time),
            create_woodsman(remaining_time),
            create_tailor(remaining_time),
            create_treasurer(remaining_time),
            create_leathersmith(remaining_time),
            create_armourer(remaining_time),
            create_theCollector(remaining_time),
            create_alchemist(remaining_time),
            create_tavernMaster(remaining_time),
            create_weaponsmith(remaining_time),
        ]
    )


def get_buy_list(ctx, msg):
    # To list the stock we need to send 3 messages.
    # 1 for starting, 1 with the actual data and the last for the end
    req = SC2S_MERCHANT_STOCK_BUY_ITEM_LIST_REQ()
    req.ParseFromString(msg)

    # TODO: handle every trader differently

    # send stage 1 (start)
    ctx.reply(SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(result=1, loopMessageFlag=1, stockList=[]))

    # send stage 2 (data the merchant is selling)
    ctx.reply(
        SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(
            result=1,
            loopMessageFlag=2,
            stockList=[
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_01",
                    stockUniqueId=1,
                    itemInfo=items.generate_bandage(),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_02",
                    stockUniqueId=2,
                    itemInfo=items.generate_torch(),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_03",
                    stockUniqueId=3,
                    itemInfo=items.generate_roundshield(),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_04",
                    stockUniqueId=4,
                    itemInfo=items.generate_lantern(),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_05",
                    stockUniqueId=5,
                    itemInfo=items.generate_sword(),
                ),
                SMERCHANT_STOCK_BUY_ITEM_INFO(
                    stockBuyId="DesignDataStockBuy:Id_StockBuy_Alchemist_06",
                    stockUniqueId=6,
                    itemInfo=items.generate_pants(),
                ),
            ],
        )
    )

    # let the protocol send stage 3
    return SS2C_MERCHANT_STOCK_BUY_ITEM_LIST_RES(result=1, loopMessageFlag=3, stockList=[])


def get_sellback_list(ctx, msg):
    # To send the items we can sell back to the merchant we need to send 3 messages.
    # 1 for starting, 1 with the actual data and the last for the end
    req = SC2S_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_REQ()
    req.ParseFromString(msg)

    # TODO: it looks like the game sends every item for every trader in this request (around 1000 items). It will do
    # this every time we change trader. Not sure if this is intended or not. For example in the data of the Alchemist
    # merchant it also sends the sellbacks for the weaponsmith.

    # send stage 1 (start)
    ctx.reply(SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES(result=1, loopMessageFlag=1, stockList=[]))

    # send stage 2 (data the merchant is selling)
    ctx.reply(
        SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES(
            result=1,
            loopMessageFlag=2,
            stockList=[
                SMERCHANT_STOCK_SELL_BACK_ITEM_INFO(
                    stockSellBackId="DesignDataStockSellBack:Id_StockSellBack_Weaponsmith", stockUniqueId=215
                )
            ],
        )
    )

    # let the protocol send stage 3
    return SS2C_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_RES(result=1, loopMessageFlag=3, stockList=[])


def create_surgeon(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Surgeon", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_santa(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Santa", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_woodsman(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Woodsman", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_tailor(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Tailor", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_treasurer(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Treasurer", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_leathersmith(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Leathersmith", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_armourer(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Armourer", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_theCollector(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_TheCollector", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_alchemist(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Alchemist", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_tavernMaster(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_TavernMaster", faction=0, remainTime=remaining_time, isUnidentified=0
    )


def create_weaponsmith(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Weaponsmith", faction=0, remainTime=remaining_time, isUnidentified=0
    )
