import os
import json
import random
from enum import Enum

# TODO We should have a list of all items as enum stored for reference to avoid misspelling mistakes

class Rarity(Enum):
    JUNK = 0
    POOR = 1
    COMMON = 2
    UNCOMMON = 3
    RARE = 4
    EPIC = 5
    LEGENDARY = 6
    UNIQUE = 7

class ItemType(Enum):
    WEAPONS = "weapons"
    ARMORS = "armors"
    JEWELRY = "jewelry"
    CONSUMABLES = "consumables"
    UTILITY = "utility"
    MATERIALS = "materials"
    LOOTABLES = "lootables"
    OTHERS = "others"

# TODO We might want to store this somewhere else, and only call it once, when server starts
json_data = {}

def loadJsonData():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for itemType in ItemType:
        type = str(itemType.value)
        path = os.path.join(current_dir, "..", "data", "items", type)
        path = os.path.abspath(path)
        files = [file for file in os.listdir(path) if file.endswith('.json')]

        if(files and len(files) > 1):
            json_data[type] = {}
            for file_name in files:
                with open(os.path.join(path, file_name), "r", encoding="utf-8") as file:
                    json_data[type][file_name] = json.load(file)

# Calls function to load all json data into json_data object
loadJsonData()

# Gets the relevant data depending on the item name and type
def getContent(name, type, rarity):
  content = {}
  dynamic_file_name = ""
  typeValue = str(type.value)
  if(type != ItemType.WEAPONS and type != ItemType.ARMORS):
      dynamic_file_name = name + "_" + rarity + "001.json"
      if dynamic_file_name in json_data.get(typeValue, {}):
        content = json_data[typeValue][dynamic_file_name][0]
  else:
      dynamic_file_name = name + ".json"
      if dynamic_file_name in json_data.get(typeValue, {}):
        content = json_data[typeValue][dynamic_file_name]

  return content

# Function to be called in order to create an item
def generateItem(name, type, rarity, itemCount):
    finalData = {}
    rarity_str = str(rarity.value)
    if(name and type):
        data = getContent(name, type, rarity_str)
        if(data):
            if(type != ItemType.WEAPONS and type != ItemType.ARMORS):
                finalData = formatOtherData(data, name, rarity_str, itemCount)
            else:
                finalData = formatData(data, name, rarity_str)
    return finalData
        
# Raw data for non weapons/armors are different, so need to be fetched differently for now
def formatOtherData(data, name, rarity, itemCount):
    finalData = {"itemId": "DesignDataItem:Id_Item_" + name + "_" + rarity + "001"}
    maxCount = int(data["Properties"]["Item"]["MaxCount"])
    if(maxCount and itemCount < maxCount):
        finalData["itemCount"] = itemCount
    return finalData

# Gets the stat properties of the item data and formats it to be consumed
def parsePropertiesToArray(data, rarity):
    properties = data["stats"][rarity]
    properties_array = []
    for key, value in properties.items():
        updatedKey = "DesignDataItemPropertyType:" + key
        properties_array.append({"propertyTypeId": updatedKey, "propertyValue": value})
    return properties_array

# Generates the stats values depending on the value ranges in the data
def adjustStatsBasedOnRanges(propertyArray):
    newPropertyArray = []
    for _, obj in enumerate(propertyArray):
        valuesArray = obj["propertyValue"]
        if(valuesArray and len(valuesArray) > 1):
            # Get range from int value
            if isinstance(valuesArray[0], int):
                random_value = random.randint(valuesArray[0], valuesArray[1])
            # Get range from percentage value
            elif isinstance(valuesArray[0], str) and '%' in valuesArray[0]:
                lower_bound = float(valuesArray[0].strip('%'))
                upper_bound = float(valuesArray[1].strip('%'))
                random_value = random.uniform(lower_bound, upper_bound)
                random_value = f"{random_value}%"
        else:
            obj["propertyValue"] = random_value
            newPropertyArray.append(obj)
    return newPropertyArray

# Formats the itemId and properties by calling other formatters, formats the response to be consumed
def formatData(data, name, rarity):
    itemId = "DesignDataItem:Id_Item_" + name + "_" + rarity + "001"
    primaryPropertyArray = adjustStatsBasedOnRanges(parsePropertiesToArray(data, rarity))
    return {
        "itemId": itemId,
        "primaryPropertyArray": primaryPropertyArray
    }
