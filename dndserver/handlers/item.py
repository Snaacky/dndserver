import json
import os
import random

from dndserver.enums.items import ItemType, Rarity

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


# Function to be called in order to create an item
def generate_new_item(name, type, rarity, item_count):
    final_data = {}
    rarity_str = str(rarity.value)
    if name and type:
        data = get_content(name, type, rarity_str)
        if data:
            if type != ItemType.WEAPONS and type != ItemType.ARMORS:
                final_data = format_other_data(data, name, rarity_str, item_count)
            else:
                final_data = format_data(data, name, rarity_str)
    return final_data


# Raw data for non weapons/armors are different, so need to be fetched differently for now
def format_other_data(data, name, rarity, item_count):
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


# Gets the stat properties of the item data and formats it to be consumed
def parse_properties_to_array(data, rarity):
    properties = data["stats"][rarity]
    properties_array = []
    for key, value in properties.items():
        updatedKey = f"DesignDataItemPropertyType:{key}"
        properties_array.append({"propertyTypeId": updatedKey, "propertyValue": value})
    return properties_array


# Generates the stats values depending on the value ranges in the data
def adjust_stats_based_on_ranges(property_array):
    new_property_array = []
    for _, obj in enumerate(property_array):
        values_array = obj["propertyValue"]
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
        else:
            obj["propertyValue"] = random_value
            new_property_array.append(obj)
    return new_property_array


# Formats the itemId and properties by calling other formatters, formats the response to be consumed
def format_data(data, name, rarity):
    item_id = f"DesignDataItem:Id_Item_{name}_{rarity}001"
    if rarity == Rarity.NONE.value:
        item_id = f"DesignDataItem:Id_Item_{name}"
    primary_property_array = adjust_stats_based_on_ranges(parse_properties_to_array(data, rarity))
    return {"itemId": item_id, "primaryPropertyArray": primary_property_array}
