from dndserver.protos import _Item_pb2 as item


def generate_torch():
    torch = item.SItem()
    torch.itemUniqueId = 6646818918302105
    torch.itemId = "DesignDataItem:Id_Item_Torch_0001"
    torch.itemCount = 1
    torch.inventoryId = 3
    torch.slotId = 13

    move_speed = item.SItemProperty()
    move_speed.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    move_speed.propertyValue = -10
    torch.primaryPropertyArray.append(move_speed)

    weapon_damage = item.SItemProperty()
    weapon_damage.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_PhysicalWeaponDamage"
    weapon_damage.propertyValue = 13
    torch.primaryPropertyArray.append(weapon_damage)

    return torch


def generate_roundshield():
    shield = item.SItem()
    shield.itemUniqueId = 6646818918302104
    shield.itemId = "DesignDataItem:Id_Item_RoundShield_0001"
    shield.itemCount = 1
    shield.inventoryId = 3
    shield.slotId = 11

    armor_rating = item.SItemProperty()
    armor_rating.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_ArmorRating"
    armor_rating.propertyValue = 13
    shield.primaryPropertyArray.append(armor_rating)

    move_speed = item.SItemProperty()
    move_speed.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    move_speed.propertyValue = -12
    shield.primaryPropertyArray.append(move_speed)

    return shield


def generate_lantern():
    lantern = item.SItem()
    lantern.itemUniqueId = 6646818918302099
    lantern.itemId = "DesignDataItem:Id_Item_Lantern_0001"
    lantern.itemCount = 1
    lantern.inventoryId = 3
    lantern.slotId = 8

    move_speed = item.SItemProperty()
    move_speed.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    move_speed.propertyValue = -10
    lantern.primaryPropertyArray.append(move_speed)

    return lantern


def generate_sword():
    sword = item.SItem()
    sword.itemUniqueId = 6646818918302103
    sword.itemId = "DesignDataItem:Id_Item_ArmingSword_0001"
    sword.itemCount = 1
    sword.inventoryId = 3
    sword.slotId = 10

    move_speed = item.SItemProperty()
    move_speed.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    move_speed.propertyValue = -20
    sword.primaryPropertyArray.append(move_speed)

    weapon_damage = item.SItemProperty()
    weapon_damage.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_PhysicalWeaponDamage"
    weapon_damage.propertyValue = 23
    sword.primaryPropertyArray.append(weapon_damage)

    return sword


def generate_pants():
    pants = item.SItem()
    pants.itemUniqueId = 6646818918302102
    pants.itemId = "DesignDataItem:Id_Item_ClothPants_0001"
    pants.itemCount = 1
    pants.inventoryId = 3
    pants.slotId = 4

    armor_rating = item.SItemProperty()
    armor_rating.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_ArmorRating"
    armor_rating.propertyValue = 8
    pants.primaryPropertyArray.append(armor_rating)

    move_speed = item.SItemProperty()
    move_speed.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    move_speed.propertyValue = -5
    pants.primaryPropertyArray.append(move_speed)

    return pants


def generate_tunic():
    tunic = item.SItem()
    tunic.itemUniqueId = 6646818918302101
    tunic.itemId = "DesignDataItem:Id_Item_AdventurerTunic_0001"
    tunic.itemCount = 1
    tunic.inventoryId = 3
    tunic.slotId = 2

    armor_rating = item.SItemProperty()
    armor_rating.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_ArmorRating"
    armor_rating.propertyValue = 14
    tunic.primaryPropertyArray.append(armor_rating)

    move_speed = item.SItemProperty()
    move_speed.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    move_speed.propertyValue = -5
    tunic.primaryPropertyArray.append(move_speed)

    return tunic


def generate_bandage():
    bandage = item.SItem()
    bandage.itemUniqueId = 6646818918302100
    bandage.itemId = "DesignDataItem:Id_Item_Bandage_0001"
    bandage.itemCount = 1
    bandage.inventoryId = 3
    bandage.slotId = 14

    primary = item.SItemProperty()
    primary.propertyTypeId = "DesignDataItemPropertyType:Id_ItemPropertyType_Effect_MoveSpeed"
    primary.propertyValue = -20
    bandage.primaryPropertyArray.append(primary)

    return bandage
