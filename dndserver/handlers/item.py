import json
import os
import random
from dndserver.enums.items import ItemType, Rarity, EnhancementWeapon, EnhancementArmor

# TODO We might want to store this somewhere else, and only call it once, when server starts
json_data = {}


def load_json_data():
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


# Gets the relevant data depending on the item name and type
def get_content(name, type, rarity):
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


# Gets the relevant data depending on the material and type
# TODO change function in order to take a list of materials
def get_content_based_on(material, item_type):
    obj = {}
    type_value = str(item_type.value)
    material_value = str(material)
    for file_name, value in json_data[type_value].items():
        if item_type != ItemType.WEAPONS and "material" in value and value["material"] == material_value:
            obj[file_name] = value
        elif item_type == ItemType.WEAPONS:
            obj[file_name] = value
    return obj


# Gets how_many random gear from a content (list of dictionaries)
def random_gear(content, how_many):
    new_result = {}
    if content:
        while len(new_result) < how_many:
            random_dict = random.choice(list(content.items()))
            random_key, random_value = random_dict
            if random_key not in new_result:
                new_result[random_key] = random_value
    return new_result


# This function generate how_many armors or weapons randomly with random quality
def random_item_list(type, material, how_many):
    final_data = []

    if type and material and how_many:
        all_gear_with = get_content_based_on(material, type)
        input_list = random_gear(all_gear_with, how_many)

        for item in input_list.keys():
            name = input_list[item]["name"]
            all_stats = input_list[item]["stats"]
            all_rarity = all_stats.keys()
            if len(all_rarity) == 0:
                continue
            random_number = random_rarity(all_rarity)
            final_data.append(format_data(input_list[item], name, random_number, type))
    return final_data


# This function produce in a proper way the rarity for gear
# gray = 50%; white = 35%; green = 24.50%; blue = 17.15%; purple = 12%;
def random_rarity(list_of_rarity):
    list_of_rarity = list(list_of_rarity)
    length = len(list_of_rarity)

    # special case when the list is empty or has length 1
    if length == 0:
        return ""
    elif length == 1:
        return list_of_rarity[0]

    list_of_chance = [50, 35, 24.5, 17.5, 12]
    return random.choices(list_of_rarity[1:-2], list_of_chance, k=1)[0]


# Function to be called in order to create an item
def generate_new_item(name, type, rarity, item_count=1):
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


# Raw data for non weapons/armors are different, so need to be fetched differently for now
def format_other_data(data, name, rarity, item_count):
    item_id = f"DesignDataItem:Id_Item_{name}_{rarity}001"
    if rarity == Rarity.NONE.value:
        item_id = f"DesignDataItem:Id_Item_{name}"
    final_data = {"itemId": item_id}
    maxCount = int(data["Properties"]["Item"]["MaxCount"])
    if maxCount and item_count < maxCount:
        final_data["itemCount"] = item_count
    return final_data


# Gets the stat properties of the item data and formats it to be consumed
def parse_properties_to_array(data, rarity):
    properties = data["stats"][rarity]
    properties_array = []
    for key, value in properties.items():
        updatedKey = f"DesignDataItemPropertyType:{key}"
        properties_array.append({"propertyTypeId": updatedKey, "propertyValue": value})
    return properties_array


# Prepare the data for secondary property to be consumed
def parse_secondary_properties_to_array(rarity, item_type):
    rarity = int(rarity)

    if rarity == Rarity.UNCOMMON.value:
        return effects_based_on(rarity, item_type)
    elif rarity == Rarity.RARE.value:
        return effects_based_on(rarity, item_type)
    elif rarity == Rarity.EPIC.value:
        return effects_based_on(rarity, item_type)
    elif rarity == Rarity.LEGENDARY.value:
        return effects_based_on(rarity, item_type)
    elif rarity == Rarity.UNIQUE.value:
        return effects_based_on(rarity, item_type)
    return []


# Helper function for parse_secondary_properties_to_array()
def effects_based_on(rarity, item_type):
    properties_array = []
    random_enhancements = [""]
    how_many_effects = [rarity-3, rarity-2]
    if item_type == ItemType.WEAPONS:
        random_enhancements = random.sample(list(EnhancementWeapon), k=random.choice(how_many_effects))
    elif item_type == ItemType.ARMORS:
        random_enhancements = random.sample(list(EnhancementArmor), k=random.choice(how_many_effects))
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


# Generates the stats values depending on the value ranges in the data
def adjust_stats_based_on_ranges(property_array):
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


# Formats the itemId and properties by calling other formatters, formats the response to be consumed
def format_data(data, name, rarity, item_type):
    item_id = f"DesignDataItem:Id_Item_{name}_{rarity}001"
    if rarity == Rarity.NONE.value:
        item_id = f"DesignDataItem:Id_Item_{name}"
    primary_property_array = adjust_stats_based_on_ranges(parse_properties_to_array(data, rarity))
    secondary_property_array = parse_secondary_properties_to_array(rarity, item_type)
    return {"itemId": item_id, "primaryPropertyArray": primary_property_array,
            "secondaryPropertyArray": secondary_property_array}
