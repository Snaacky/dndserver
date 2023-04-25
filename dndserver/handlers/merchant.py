from dndserver.protos.Merchant import SS2C_MERCHANT_LIST_RES, SMERCHANT_INFO


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


def create_surgeon(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Surgeon",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_santa(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Santa",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_woodsman(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Woodsman",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_tailor(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Tailor",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_treasurer(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Treasurer",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_leathersmith(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Leathersmith",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_armourer(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Armourer",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_theCollector(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_TheCollector",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_alchemist(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Alchemist",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_tavernMaster(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_TavernMaster",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )


def create_weaponsmith(remaining_time) -> SMERCHANT_INFO:
    return SMERCHANT_INFO(
        merchantId="DesignDataMerchant:Id_Merchant_Weaponsmith",
        faction=0,
        remainTime=remaining_time,
        isUnidentified=0
    )
