from enum import Enum


class BanType(Enum):
    FAIL_LOGIN_BAN_USER = 12
    FAIL_LOGIN_BAN_USER_CHEATER = 13
    FAIL_LOGIN_BAN_USER_INAPPROPRIATE_NAME = 14
    FAIL_LOGIN_BAN_USER_ETC = 15
    FAIL_LOGIN_BAN_HARDWARE = 16


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
