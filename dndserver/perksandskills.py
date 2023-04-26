from dndserver.enums import CharacterClass

perks_barbarian = [
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

perks_bard = [
    "DesignDataPerk:Id_Perk_LoreMastery",
    "DesignDataPerk:Id_Perk_MelodicProtection",
    "DesignDataPerk:Id_Perk_RapierMastery",
    "DesignDataPerk:Id_Perk_WanderersLuck",
    "DesignDataPerk:Id_Perk_WarSong",
]

perks_cleric = [
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

perks_fighter = [
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

perks_ranger = [
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

perks_rogue = [
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

perks_wizard = [
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
    CharacterClass.BARBARIAN: perks_barbarian,
    CharacterClass.BARD: perks_bard,
    CharacterClass.CLERIC: perks_cleric,
    CharacterClass.FIGHTER: perks_fighter,
    CharacterClass.RANGER: perks_ranger,
    CharacterClass.ROGUE: perks_rogue,
    CharacterClass.WIZARD: perks_wizard,
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


skills_barbarian = [
    "DesignDataSkill:Id_Skill_Rage",
    "DesignDataSkill:Id_Skill_RecklessAttack",
    "DesignDataSkill:Id_Skill_SavageRoar",
    "DesignDataSkill:Id_Skill_WarCry",
    "DesignDataSkill:Id_Skill_AchillesStrike",
    "DesignDataSkill:Id_Skill_BloodExchange",
    "DesignDataSkill:Id_Skill_LifeSiphon",
]

skills_bard = [
    "DesignDataSkill:Id_Skill_Encore",
    "DesignDataSkill:Id_Skill_Dissonance",
    "DesignDataSkill:Id_Skill_MusicMemory1",
    "DesignDataSkill:Id_Skill_MusicMemory2",
]

skills_cleric = [
    "DesignDataSkill:Id_Skill_HolyPurification",
    "DesignDataSkill:Id_Skill_Judgement",
    "DesignDataSkill:Id_Skill_Smite",
    "DesignDataSkill:Id_Skill_SpellMemory1",
    "DesignDataSkill:Id_Skill_SpellMemory2",
    "DesignDataSkill:Id_Skill_DivineProtection",
]

skills_fighter = [
    "DesignDataSkill:Id_Skill_AdrenalineRush",
    "DesignDataSkill:Id_Skill_Breakthrough",
    "DesignDataSkill:Id_Skill_SecondWind",
    "DesignDataSkill:Id_Skill_Sprint",
    "DesignDataSkill:Id_Skill_Taunt",
    "DesignDataSkill:Id_Skill_VictoryStrike",
    "DesignDataSkill:Id_Skill_PerfectBlock",
    "DesignDataSkill:Id_Skill_ShieldSlam",
]

skills_ranger = [
    "DesignDataSkill:Id_Skill_FieldRation",
    "DesignDataSkill:Id_Skill_MultiShot",
    "DesignDataSkill:Id_Skill_QuickFire",
    "DesignDataSkill:Id_Skill_QuickShot",
    "DesignDataSkill:Id_Skill_TrueShot",
    "DesignDataSkill:Id_Skill_ForcefulShot",
    "DesignDataSkill:Id_Skill_PenetratingShot",
]

skills_rogue = [
    "DesignDataSkill:Id_Skill_Caltrop",
    "DesignDataSkill:Id_Skill_Hide",
    "DesignDataSkill:Id_Skill_Rupture",
    "DesignDataSkill:Id_Skill_SmokeBomb",
    "DesignDataSkill:Id_Skill_WeakpointAttack",
    "DesignDataSkill:Id_Skill_CutThroat",
    "DesignDataSkill:Id_Skill_Tumbling",
]

skills_wizard = [
    "DesignDataSkill:Id_Skill_IntenseFocus",
    "DesignDataSkill:Id_Skill_Meditation",
    "DesignDataSkill:Id_Skill_SpellMemory1",
    "DesignDataSkill:Id_Skill_SpellMemory2",
    "DesignDataSkill:Id_Skill_ArcaneShield",
]

skills = {
    CharacterClass.BARBARIAN: skills_barbarian,
    CharacterClass.BARD: skills_bard,
    CharacterClass.CLERIC: skills_cleric,
    CharacterClass.FIGHTER: skills_fighter,
    CharacterClass.RANGER: skills_ranger,
    CharacterClass.ROGUE: skills_rogue,
    CharacterClass.WIZARD: skills_wizard,
}

# unused skills
# "DesignDataSkill:Id_Skill_SmokePot"
