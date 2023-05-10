from dndserver.enums.classes import CharacterClass


cleric = [
    "DesignDataSpell:Id_Spell_HolyLight",
    "DesignDataSpell:Id_Spell_HolyStrike",
    "DesignDataSpell:Id_Spell_LesserHeal",
    "DesignDataSpell:Id_Spell_LocustsSwarm",
    "DesignDataSpell:Id_Spell_Protection",
    "DesignDataSpell:Id_Spell_Resurrection",
    "DesignDataSpell:Id_Spell_Sanctuary",
    "DesignDataSpell:Id_Spell_BindEvil",
    "DesignDataSpell:Id_Spell_Bless",
    "DesignDataSpell:Id_Spell_Cleanse",
    "DesignDataSpell:Id_Spell_DivineStrike",
    "DesignDataSpell:Id_Spell_Earthquake",
]

wizard = [
    "DesignDataSpell:Id_Spell_Fireball",
    "DesignDataSpell:Id_Spell_Haste",
    "DesignDataSpell:Id_Spell_IceBolt",
    "DesignDataSpell:Id_Spell_Ignite",
    "DesignDataSpell:Id_Spell_Invisibility",
    "DesignDataSpell:Id_Spell_Light",
    "DesignDataSpell:Id_Spell_LightningStrike",
    "DesignDataSpell:Id_Spell_Lazy",
    "DesignDataSpell:Id_Spell_Zap",
    "DesignDataSpell:Id_Spell_MagicMissile",
    "DesignDataSpell:Id_Spell_ChainLightning",
]

spells = {
    CharacterClass.CLERIC: cleric,
    CharacterClass.WIZARD: wizard,
}
