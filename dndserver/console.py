import sys
from dndserver.objects import items
from dndserver.enums.items import ItemType, Rarity, Item as ItemEnum
from dndserver.models import Item
from dndserver.utils import get_user


def list_items(filter=None):
    for key in ItemEnum:
        if filter is not None and filter.upper() in key.name:
            print(key.name)
        elif not filter:
            print(key.name)


def list_rarity(filter=None):
    for key in Rarity:
        if filter is not None and filter in key.name:
            print(key.name)
        elif not filter:
            print(key.name)


def help():
    print("List of available commands:")
    for _, info in commands.items():
        print(info["help"])


def give_item(user, item_name, item_type, rarity=Rarity.NONE, amount=1):
    _, userAccount = get_user(nickname=user)
    if not userAccount:
        print("User is not online")
        return
    item = items.generate_item(ItemEnum[item_name], ItemType[item_type], Rarity[rarity], 4, 0, amount)
    if not item.itemId:
        print("Error: Item may not be valid")
        return
    it = Item()
    it.character_id = userAccount.character.id
    it.item_id = item.itemId
    it.quantity = item.itemCount
    it.inventory_id = item.inventoryId
    it.slot_id = item.slotId
    it.save()


def exit():
    sys.exit(0)


commands = {
    "/help": {"function": help, "help": ""},
    "/give_item": {"function": give_item, "help": "/give_item <user> <item_name> <rarity> [amount]"},
    "/list_items": {"function": list_items, "help": "/list_items [filter]"},
    "/list_rarity": {"function": list_rarity, "help": "/list_rarity [filter]"},
    "/exit": {"function": exit, "help": "/exit"}
    # add more commands here
}


def console():
    line = None
    while True:
        try:
            line = input("> ")
        except EOFError:
            pass

        if not line:
            return
        parts = line.split()

        if parts[0] not in commands:
            print("Invalid command. Type /help to get the list of commands")
            continue

        try:
            commands[parts[0]]["function"](*parts[1:])
        except TypeError:
            print(f"Invalid command. Usage: {commands[parts[0]]['help']}")
