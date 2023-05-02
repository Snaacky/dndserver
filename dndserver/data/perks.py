from dndserver.enums.classes import CharacterClass


level_requirements = [1, 5, 10, 15]

barbarian = [
    "DesignDataPerk:Id_Perk_AxeSpecialization",
    "DesignDataPerk:Id_Perk_Berserker",
    "DesignDataPerk:Id_Perk_Carnage",
    "DesignDataPerk:Id_Perk_IronWill",
    "DesignDataPerk:Id_Perk_MoraleBoost",
    "DesignDataPerk:Id_Perk_Savage",
    "DesignDataPerk:Id_Perk_Crush",
    "DesignDataPerk:Id_Perk_Robust",
    "DesignDataPerk:Id_Perk_TwoHander",
    "DesignDataPerk:Id_Perk_PotionChugger",
    "DesignDataPerk:Id_Perk_Executioner",
]

bard = [
    "DesignDataPerk:Id_Perk_LoreMastery",
    "DesignDataPerk:Id_Perk_MelodicProtection",
    "DesignDataPerk:Id_Perk_RapierMastery",
    "DesignDataPerk:Id_Perk_WanderersLuck",
    "DesignDataPerk:Id_Perk_WarSong",
]

cleric = [
    "DesignDataPerk:Id_Perk_AdvancedHealer",
    "DesignDataPerk:Id_Perk_BluntWeaponMastery",
    "DesignDataPerk:Id_Perk_Brewmaster",
    "DesignDataPerk:Id_Perk_Kindness",
    "DesignDataPerk:Id_Perk_Perseverance",
    "DesignDataPerk:Id_Perk_ProtectionfromEvil",
    "DesignDataPerk:Id_Perk_Requiem",
    "DesignDataPerk:Id_Perk_UndeadSlaying",
    "DesignDataPerk:Id_Perk_HolyAura",
]

fighter = [
    "DesignDataPerk:Id_Perk_Barricade",
    "DesignDataPerk:Id_Perk_ComboAttack",
    "DesignDataPerk:Id_Perk_Counterattack",
    "DesignDataPerk:Id_Perk_DefenseExpert",
    "DesignDataPerk:Id_Perk_DualWield",
    "DesignDataPerk:Id_Perk_ProjectileResistance",
    "DesignDataPerk:Id_Perk_ShieldExpert",
    "DesignDataPerk:Id_Perk_Swift",
    "DesignDataPerk:Id_Perk_WeaponMastery",
    "DesignDataPerk:Id_Perk_AdrenalineSpike",
    "DesignDataPerk:Id_Perk_Slayer",
]

ranger = [
    "DesignDataPerk:Id_Perk_CrossbowMastery",
    "DesignDataPerk:Id_Perk_EnhancedHearing",
    "DesignDataPerk:Id_Perk_Kinesthesia",
    "DesignDataPerk:Id_Perk_NimbleHands",
    "DesignDataPerk:Id_Perk_RangedWeaponsExpert",
    "DesignDataPerk:Id_Perk_Sharpshooter",
    "DesignDataPerk:Id_Perk_SpearProficiency",
    "DesignDataPerk:Id_Perk_Tracking",
    "DesignDataPerk:Id_Perk_TrapExpert",
    "DesignDataPerk:Id_Perk_CripplingShot",
    "DesignDataPerk:Id_Perk_QuickReload",
]

rogue = [
    "DesignDataPerk:Id_Perk_Ambush",
    "DesignDataPerk:Id_Perk_BackAttack",
    "DesignDataPerk:Id_Perk_Creep",
    "DesignDataPerk:Id_Perk_DaggerExpert",
    "DesignDataPerk:Id_Perk_HiddenPocket",
    "DesignDataPerk:Id_Perk_LockpickSet",
    "DesignDataPerk:Id_Perk_Pickpocket",
    "DesignDataPerk:Id_Perk_PoisonedWeapon",
    "DesignDataPerk:Id_Perk_Stealth",
    "DesignDataPerk:Id_Perk_TrapDetection",
    "DesignDataPerk:Id_Perk_DoubleJump",
    "DesignDataPerk:Id_Perk_Jokester",
    "DesignDataPerk:Id_Perk_ShadowRunner",
    "DesignDataPerk:Id_Perk_Thrust",
]

wizard = [
    "DesignDataPerk:Id_Perk_ArcaneFeedback",
    "DesignDataPerk:Id_Perk_ArcaneMastery",
    "DesignDataPerk:Id_Perk_FireMastery",
    "DesignDataPerk:Id_Perk_IceShield",
    "DesignDataPerk:Id_Perk_ManaSurge",
    "DesignDataPerk:Id_Perk_Melt",
    "DesignDataPerk:Id_Perk_QuickChant",
    "DesignDataPerk:Id_Perk_ReactiveShield",
    "DesignDataPerk:Id_Perk_Sage",
]

perks = {
    CharacterClass.BARBARIAN: barbarian,
    CharacterClass.BARD: bard,
    CharacterClass.CLERIC: cleric,
    CharacterClass.FIGHTER: fighter,
    CharacterClass.RANGER: ranger,
    CharacterClass.ROGUE: rogue,
    CharacterClass.WIZARD: wizard,
}

# Other items. Not used at the moment.
# DesignDataPerk:Id_Perk_Chase
# DesignDataPerk:Id_Perk_DaggerMastery
# DesignDataPerk:Id_Perk_LockpickingMastery
# DesignDataPerk:Id_Perk_Backstab
# DesignDataPerk:Id_Perk_TwoHandedWeaponExpert
# DesignDataPerk:Id_Perk_Malice
# DesignDataPerk:Id_Perk_Toughness
# DesignDataPerk:Id_Perk_Smash
# DesignDataPerk:Id_Perk_RangedWeaponsMastery
# DesignDataPerk:Id_Perk_ShieldMastery
# DesignDataPerk:Id_Perk_DefenseMastery
# DesignDataPerk:Id_Perk_SurvivalistTongue
# DesignDataPerk:Id_Perk_TrapMastery
