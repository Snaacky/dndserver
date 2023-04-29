from dndserver.enums.classes import CharacterClass


barbarian = [
    "DesignDataSkill:Id_Skill_Rage",
    "DesignDataSkill:Id_Skill_RecklessAttack",
    "DesignDataSkill:Id_Skill_SavageRoar",
    "DesignDataSkill:Id_Skill_WarCry",
    "DesignDataSkill:Id_Skill_AchillesStrike",
    "DesignDataSkill:Id_Skill_BloodExchange",
    "DesignDataSkill:Id_Skill_LifeSiphon",
]

bard = [
    "DesignDataSkill:Id_Skill_Encore",
    "DesignDataSkill:Id_Skill_Dissonance",
    "DesignDataSkill:Id_Skill_MusicMemory1",
    "DesignDataSkill:Id_Skill_MusicMemory2",
]

cleric = [
    "DesignDataSkill:Id_Skill_HolyPurification",
    "DesignDataSkill:Id_Skill_Judgement",
    "DesignDataSkill:Id_Skill_Smite",
    "DesignDataSkill:Id_Skill_SpellMemory1",
    "DesignDataSkill:Id_Skill_SpellMemory2",
    "DesignDataSkill:Id_Skill_DivineProtection",
]

fighter = [
    "DesignDataSkill:Id_Skill_AdrenalineRush",
    "DesignDataSkill:Id_Skill_Breakthrough",
    "DesignDataSkill:Id_Skill_SecondWind",
    "DesignDataSkill:Id_Skill_Sprint",
    "DesignDataSkill:Id_Skill_Taunt",
    "DesignDataSkill:Id_Skill_VictoryStrike",
    "DesignDataSkill:Id_Skill_PerfectBlock",
    "DesignDataSkill:Id_Skill_ShieldSlam",
]

ranger = [
    "DesignDataSkill:Id_Skill_FieldRation",
    "DesignDataSkill:Id_Skill_MultiShot",
    "DesignDataSkill:Id_Skill_QuickFire",
    "DesignDataSkill:Id_Skill_QuickShot",
    "DesignDataSkill:Id_Skill_TrueShot",
    "DesignDataSkill:Id_Skill_ForcefulShot",
    "DesignDataSkill:Id_Skill_PenetratingShot",
]

rogue = [
    "DesignDataSkill:Id_Skill_Caltrop",
    "DesignDataSkill:Id_Skill_Hide",
    "DesignDataSkill:Id_Skill_Rupture",
    "DesignDataSkill:Id_Skill_SmokeBomb",
    "DesignDataSkill:Id_Skill_WeakpointAttack",
    "DesignDataSkill:Id_Skill_CutThroat",
    "DesignDataSkill:Id_Skill_Tumbling",
]

wizard = [
    "DesignDataSkill:Id_Skill_IntenseFocus",
    "DesignDataSkill:Id_Skill_Meditation",
    "DesignDataSkill:Id_Skill_SpellMemory1",
    "DesignDataSkill:Id_Skill_SpellMemory2",
    "DesignDataSkill:Id_Skill_ArcaneShield",
]

skills = {
    CharacterClass.BARBARIAN: barbarian,
    CharacterClass.BARD: bard,
    CharacterClass.CLERIC: cleric,
    CharacterClass.FIGHTER: fighter,
    CharacterClass.RANGER: ranger,
    CharacterClass.ROGUE: rogue,
    CharacterClass.WIZARD: wizard,
}

# unused skills
# "DesignDataSkill:Id_Skill_SmokePot"
