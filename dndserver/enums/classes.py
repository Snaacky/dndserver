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