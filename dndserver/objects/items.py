from dndserver.protos import Item as item
from dndserver.handlers.item import generateItem

class Item:
    def __init__(
        self,
        unique_id: int,
        item_id: str,
        item_count: int,
        inventory_id: int,
        slot_id: int,
        primary_properties: list[tuple[str, int]],
    ) -> None:
        self.unique_id = unique_id
        self.item_id = item_id
        self.item_count = item_count
        self.inventory_id = inventory_id
        self.slot_id = slot_id
        self.primary_properties = primary_properties

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

# TODO The name should probably be in an ENUM that contains all item names available
def generate_item(name, type, rarity, inventoryId, slotId, itemCount = 1, uniqueId = None):
    newItem = item.SItem()
    newItem.inventoryId = inventoryId
    newItem.slotId = slotId

    # TODO Remove uniqueId from arguments, only here temporary for the merchant items
    if uniqueId is not None:
        newItem.itemUniqueId = uniqueId

    itemValues = generateItem(name, type, rarity, itemCount)
    if(itemValues):
        newItem.itemId = itemValues["itemId"]
        newItem.itemCount = int(itemValues.get("itemCount", itemCount))
        propertiesArray = itemValues.get("primaryPropertyArray", [])
        if(propertiesArray and len(propertiesArray) > 1):
            for property in itemValues["primaryPropertyArray"]:
                itemProperty = item.SItemProperty()
                itemProperty.propertyTypeId = property["propertyTypeId"]
                itemProperty.propertyValue = property["propertyValue"]
                newItem.primaryPropertyArray.append(itemProperty)
    return newItem


def generate_reckless():
    skills = item.SSkill()
    skills.index = 1
    skills.skillId = "DesignDataSkill:Id_Skill_RecklessAttack"
    return skills


def generate_adrenaline():
    skills = item.SSkill()
    skills.index = 2
    skills.skillId = "DesignDataSkill:Id_Skill_AdenalineRush"
    return skills


def generate_two_hander():
    skills = item.SPerk()
    skills.index = 1
    skills.perkId = "DesignDataPerk:Id_Perk_TwoHander"
    return skills
