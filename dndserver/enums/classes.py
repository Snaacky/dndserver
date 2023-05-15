from enum import Enum


class CharacterClass(Enum):
    BARBARIAN = "DesignDataPlayerCharacter:Id_PlayerCharacter_Barbarian"
    BARD = "DesignDataPlayerCharacter:Id_PlayerCharacter_Bard"
    CLERIC = "DesignDataPlayerCharacter:Id_PlayerCharacter_Cleric"
    FIGHTER = "DesignDataPlayerCharacter:Id_PlayerCharacter_Fighter"
    RANGER = "DesignDataPlayerCharacter:Id_PlayerCharacter_Ranger"
    ROGUE = "DesignDataPlayerCharacter:Id_PlayerCharacter_Rogue"
    WIZARD = "DesignDataPlayerCharacter:Id_PlayerCharacter_Wizard"
    NONE = ""


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class MerchantClass(Enum):
    SURGEON = "DesignDataMerchant:Id_Merchant_Surgeon"
    SANTA = "DesignDataMerchant:Id_Merchant_Santa"
    WOODSMAN = "DesignDataMerchant:Id_Merchant_Woodsman"
    TAILOR = "DesignDataMerchant:Id_Merchant_Tailor"
    TREASURER = "DesignDataMerchant:Id_Merchant_Treasurer"
    LEATHERSMITH = "DesignDataMerchant:Id_Merchant_Leathersmith"
    ARMOURER = "DesignDataMerchant:Id_Merchant_Armourer"
    THECOLLECTOR = "DesignDataMerchant:Id_Merchant_TheCollector"
    ALCHEMIST = "DesignDataMerchant:Id_Merchant_Alchemist"
    TAVERNMASTER = "DesignDataMerchant:Id_Merchant_TavernMaster"
    WEAPONSMITH = "DesignDataMerchant:Id_Merchant_Weaponsmith"
    GOBLINMERCHANT = "DesignDataMerchant:Id_Merchant_GoblinMerchant"
    VALENTINE = "DesignDataMerchant:Id_Merchant_Valentine"
    PUMPKINMAN = "DesignDataMerchant:Id_Merchant_PumpkinMan"
