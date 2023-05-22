import json
import os
import random
from typing import List, Dict, Any

from dndserver.enums.items import (
    ItemType,
    Rarity,
    EnhancementPhysicalWeapon,
    EnhancementMagicWeapon,
    MagicWeapon,
    EnhancementArmor,
    Material,
)

# TODO We might want to store this somewhere else, and only call it once, when server starts
json_data = {}


def load_json_data() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for item_type in ItemType:
        type = str(item_type.value)
        path = os.path.join(current_dir, "..", "data", "items", type)
        final_path = os.path.abspath(path)
        files = [file for file in os.listdir(final_path) if file.endswith(".json")]
        if len(files) > 0:
            json_data[type] = {}
            for file_name in files:
                with open(os.path.join(final_path, file_name), "r", encoding="utf-8") as file:
                    json_data[type][file_name] = json.load(file)


# Calls function to load all json data into json_data object
load_json_data()


def get_content(name: str, type: ItemType, rarity: Rarity) -> dict:
    """Gets the relevant data depending on the item name and type"""

    content = {}
    dynamic_file_name = ""
    typeValue = str(type.value)
    file_name_no_rarity = f"{name}.json"
    if rarity == Rarity.NONE.value:
        if file_name_no_rarity in json_data.get(typeValue, None):
            content = json_data[typeValue][file_name_no_rarity][0]
    elif type != ItemType.WEAPONS and type != ItemType.ARMORS:
        dynamic_file_name = f"{name}_{rarity}001.json"
        if dynamic_file_name in json_data.get(typeValue, None):
            content = json_data[typeValue][dynamic_file_name][0]
    else:
        if file_name_no_rarity in json_data.get(typeValue, None):
            content = json_data[typeValue][file_name_no_rarity]
    return content


def get_content_based_on(material: Material, item_type: ItemType) -> Dict[str, Any]:
    """Gets the relevant data depending on the material and type"""

    obj = {}
    type_value = str(item_type.value)
    material_value = str(material)
    for file_name, value in json_data[type_value].items():
        if item_type != ItemType.WEAPONS and "material" in value and value["material"] == material_value:
            obj[file_name] = value
        elif item_type == ItemType.WEAPONS:
            obj[file_name] = value
    return obj


def random_gear(content: dict, how_many: int) -> dict:
    """Return a random dictionary of how many items you want from a list of dictionaries (content)"""

    new_result = {}
    if content:
        while len(new_result) < how_many:
            random_dict = random.choice(list(content.items()))
            random_key, random_value = random_dict
            if random_key not in new_result:
                new_result[random_key] = random_value
    return new_result


def random_item_list(type: ItemType, material: Material, item_count: int) -> List[Dict[str, Any]]:
    """Produce a list of random weapon or armor for merchants"""
    final_data = []

    if type and material and item_count:
        all_gear_with = get_content_based_on(material, type)
        input_list = random_gear(all_gear_with, item_count)

        for item in input_list.keys():
            name = input_list[item]["name"]
            all_stats = input_list[item]["stats"]
            all_rarity = all_stats.keys()
            if len(all_rarity) == 0:
                continue
            random_number = random_rarity(all_rarity)
            final_data.append(format_data(input_list[item], name, random_number, type))
    return final_data


def random_rarity(list_of_rarity: List[Rarity]) -> Rarity:
    """Produce a random rarity for gear:
    gray = 45%; white = 35%; green = 24.50%; blue = 15.50%; purple = 8%;"""

    list_of_rarity = list(list_of_rarity)
    length = len(list_of_rarity)

    # special case when the list is empty or has length 1
    if length == 0:
        return ""
    elif length == 1:
        return list_of_rarity[0]

    list_of_chance = [45, 35, 24.5, 15.5, 8]
    return random.choices(list_of_rarity[1:-2], list_of_chance, k=1)[0]


def generate_new_item(name: str, type: ItemType, rarity: Rarity, item_count: int = 1) -> dict[str, Any]:
    """Function to be called in order to create an item"""

    final_data = {}
    rarity_str = str(rarity.value)
    if name and type:
        data = get_content(name, type, rarity_str)
        if data:
            if type != ItemType.WEAPONS and type != ItemType.ARMORS:
                final_data = format_other_data(data, name, rarity_str, item_count)
            else:
                final_data = format_data(data, name, rarity_str, type)
    return final_data


def format_other_data(data: dict, name: str, rarity: Rarity, item_count: int) -> Dict[str, str]:
    """Raw data for non weapons/armors are different, so need to be fetched differently"""

    item_id = f"DesignDataItem:Id_Item_{name}_{rarity}001"
    if rarity == Rarity.NONE.value:
        item_id = f"DesignDataItem:Id_Item_{name}"
    final_data = {"itemId": item_id}
    maxCount = int(data["Properties"]["Item"]["MaxCount"])
    if maxCount and int(item_count) <= maxCount:
        final_data["itemCount"] = int(item_count)
    else:
        final_data["itemCount"] = maxCount
    return final_data


def parse_properties_to_array(data: dict, rarity: str) -> List[dict]:
    """Gets the stat properties of the item data and formats it to be consumed"""

    properties = data["stats"][rarity]
    properties_array = []
    for key, value in properties.items():
        updatedKey = f"DesignDataItemPropertyType:{key}"
        properties_array.append({"propertyTypeId": updatedKey, "propertyValue": value})
    return properties_array


def parse_secondary_properties_to_array(rarity: str, item_type: ItemType, name: str) -> List[dict]:
    """Prepare the data for secondary property to be consumed"""
    rarity = int(rarity)

    if rarity == Rarity.UNCOMMON.value:
        return effects_based_on(rarity, item_type, name)
    elif rarity == Rarity.RARE.value:
        return effects_based_on(rarity, item_type, name)
    elif rarity == Rarity.EPIC.value:
        return effects_based_on(rarity, item_type, name)
    elif rarity == Rarity.LEGENDARY.value:
        return effects_based_on(rarity, item_type, name)
    elif rarity == Rarity.UNIQUE.value:
        return effects_based_on(rarity, item_type, name)
    return []


def effects_based_on(rarity: str, item_type: ItemType, name: str) -> List[dict]:
    """Select random sencondary effects for weapons and armors"""

    properties_array = []
    random_enhancements = [""]
    number = random.choices([rarity - 3, rarity - 2], [5, 95], k=1)[0]
    if number == 0:
        return properties_array

    if item_type == ItemType.WEAPONS:
        if (name in weapon.value for weapon in MagicWeapon):
            weapon_enha = list(EnhancementMagicWeapon)
        else:
            weapon_enha = list(EnhancementPhysicalWeapon)
        random_enhancements = random.sample(weapon_enha, k=number)
    elif item_type == ItemType.ARMORS:
        armor_enha = list(EnhancementArmor)
        random_enhancements = random.sample(armor_enha, k=number)

    if not random_enhancements:
        return properties_array

    for enha in random_enhancements:
        if str(enha).find("._") != -1:
            random_value = random.randrange(9, 50)
        else:
            random_value = random.randrange(1, 4)
        updatedKey = f"DesignDataItemPropertyType:Id_ItemPropertyType_{enha.value}"
        properties_array.append({"propertyTypeId": updatedKey, "propertyValue": random_value})

    return properties_array


def adjust_stats_based_on_ranges(property_array: List[dict]) -> List[dict]:
    """Generates the stats values depending on the value ranges in the data"""

    new_property_array = []
    for _, obj in enumerate(property_array):
        values_array = obj["propertyValue"]
        # default value for fallback
        random_value = 1
        if values_array and len(values_array) > 1:
            # Get range from int value
            if isinstance(values_array[0], int):
                random_value = random.randint(values_array[0], values_array[1])
            # Get range from percentage value
            elif isinstance(values_array[0], str) and "%" in values_array[0]:
                lower_bound = float(values_array[0].strip("%"))
                upper_bound = float(values_array[1].strip("%"))
                random_value = random.uniform(lower_bound, upper_bound)
                random_value = f"{random_value}%"
            obj["propertyValue"] = random_value
            new_property_array.append(obj)
        else:
            obj["propertyValue"] = random_value
            new_property_array.append(obj)
    return new_property_array


def format_data(data: dict, name: str, rarity: str, item_type: ItemType) -> dict:
    """Formats the itemId and properties by calling other formatters, formats the response to be consumed"""

    item_id = f"DesignDataItem:Id_Item_{name}_{rarity}001"
    if rarity == Rarity.NONE.value:
        item_id = f"DesignDataItem:Id_Item_{name}"
    primary_property_array = adjust_stats_based_on_ranges(parse_properties_to_array(data, rarity))
    secondary_property_array = parse_secondary_properties_to_array(rarity, item_type, name)
    return {
        "itemId": item_id,
        "primaryPropertyArray": primary_property_array,
        "secondaryPropertyArray": secondary_property_array,
    }
