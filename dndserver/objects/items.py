from typing import Tuple, List, Any

from dndserver.handlers import item as hItem
from dndserver.protos import Item as item
from dndserver.data import merchant
from dndserver.enums.items import ItemType, Material, Rarity, Item as ItemEnum
from dndserver.enums.classes import MerchantClass
from dndserver.protos.Defines import Define_Item, Define_Equipment


class Item:
    def __init__(
        self,
        unique_id: int,
        item_id: str,
        item_count: int,
        inventory_id: int,
        slot_id: int,
        primary_properties: list[tuple[str, int]],
        secondary_properties: list[tuple[str, int]],
    ) -> None:
        self.unique_id = unique_id
        self.item_id = item_id
        self.item_count = item_count
        self.inventory_id = inventory_id
        self.slot_id = slot_id
        self.primary_properties = primary_properties
        self.secondary_properties = secondary_properties

    def create(self):
        new_item = item.SItem()
        new_item.itemUniqueId = self.unique_id
        new_item.itemId = self.item_id
        new_item.itemCount = self.item_count
        new_item.inventoryId = self.inventory_id
        new_item.slotId = self.slot_id
        for prop in self.primary_properties:
            new_prop = new_item.SItemProperty()
            new_prop.propertyTypeId = prop[0]
            new_prop.propertyValue = prop[1]
            new_item.primaryPropertyArray.append(new_prop)

        for prop in self.secondary_properties:
            new_prop = new_item.SItemProperty()
            new_prop.propertyTypeId = prop[0]
            new_prop.propertyValue = prop[1]
            new_item.secondaryPropertyArray.append(new_prop)


def generate_item(
    name: ItemEnum,
    type: ItemType,
    rarity: Rarity,
    inventoryId: Define_Item.InventoryId,
    slotId: Define_Equipment.SlotId,
    item_count: int = 1,
) -> item.SItem:
    return item_parser(hItem.generate_new_item(name.value, type, rarity, item_count), inventoryId, slotId, item_count)


def item_parser(
    item_values: dict[str, Any], inventoryId: Define_Item.InventoryId, slotId: Define_Equipment.SlotId, item_count: int
) -> item.SItem:
    newItem = item.SItem()
    newItem.inventoryId = inventoryId
    newItem.slotId = slotId
    newItem.itemId = item_values["itemId"]
    newItem.itemCount = int(item_values.get("itemCount", item_count))

    propertiesArray = item_values.get("primaryPropertyArray", [])
    if propertiesArray and len(propertiesArray) >= 1:
        for property in item_values["primaryPropertyArray"]:
            itemProperty = item.SItemProperty()
            itemProperty.propertyTypeId = property["propertyTypeId"]
            if type(property["propertyValue"]) == str:
                itemProperty.propertyValue = int(property["propertyValue"][:-3]) * 10
            else:
                itemProperty.propertyValue = property["propertyValue"]
            newItem.primaryPropertyArray.append(itemProperty)
    propertiesArray = item_values.get("secondaryPropertyArray", [])
    if propertiesArray and len(propertiesArray) >= 1:
        for property in item_values["secondaryPropertyArray"]:
            itemProperty = item.SItemProperty()
            itemProperty.propertyTypeId = property["propertyTypeId"]
            itemProperty.propertyValue = property["propertyValue"]
            newItem.secondaryPropertyArray.append(itemProperty)

    return newItem


def generate_random_item(merch_id: MerchantClass, amount: int) -> List[Tuple[item.SItem, int]]:
    ret = []

    # TODO: Add Merchants when we know what they sell
    if merch_id == MerchantClass.ARMOURER:
        item_type = ItemType.ARMORS
        material = Material.PLATE
    elif merch_id == MerchantClass.WEAPONSMITH:
        item_type = ItemType.WEAPONS
        material = Material.NONE
    elif merch_id == MerchantClass.SURGEON:
        item_type = ItemType.UTILITY
        material = Material.NONE
    elif merch_id == MerchantClass.WOODSMAN:
        item_type = ItemType.UTILITY
        material = Material.NONE
    elif merch_id == MerchantClass.ALCHEMIST:
        item_type = ItemType.UTILITY
        material = Material.NONE
    elif merch_id == MerchantClass.LEATHERSMITH:
        item_type = ItemType.ARMORS
        material = Material.LEATHER
    elif merch_id == MerchantClass.TAILOR:
        item_type = ItemType.ARMORS
        material = Material.CLOTH
    elif merch_id == MerchantClass.GOBLINMERCHANT:
        item_type = ItemType.ARMORS
        material = Material.LEATHER
    elif merch_id == MerchantClass.SANTA:
        item_type = ItemType.UTILITY
        material = Material.NONE
    elif merch_id == MerchantClass.PUMPKINMAN:
        item_type = ItemType.UTILITY
        material = Material.NONE
    else:
        return ret

    items = hItem.random_item_list(item_type, material.value, amount)
    for i in items:
        ret.append((item_parser(i, 1, 1, 1), 1))

    # Sorting the items per rarity only becouse ATM the last items in the merch have higher price
    sorted_ret = sorted(ret, key=lambda x: sum([int(c) for c in x[0].itemId[-4:] if c.isdigit()]))

    return sorted_ret


def generate_merch_items(merch_id: MerchantClass) -> List[Tuple[item.SItem, int]]:
    items = merchant.fixed_items[merch_id]
    ret = []

    for item_merch in items:
        newItem = item.SItem()
        newItem.itemId = item_merch[0]
        newItem.itemCount = item_merch[1]
        ret.append((newItem, item_merch[2]))

    return ret + generate_random_item(merch_id, len(merchant.buy_mapping[merch_id]) - len(items))
