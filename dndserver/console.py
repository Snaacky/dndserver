import sys
from dndserver.objects import items
from dndserver.enums.items import ItemType, Rarity, Item as ItemEnum
from dndserver.models import Item
from dndserver.utils import get_user
from dndserver.handlers.friends import count_friends
from loguru import logger


def enum(type, filter=None):
    keys = []
    if type == "rarity":
        for key in Rarity:
            if filter is not None and filter in key.name:
                keys.append(key.name)
            elif not filter:
                keys.append(key.name)
    elif type == "items":
        for key in ItemEnum:
            if filter is not None and filter.upper() in key.name:
                keys.append(key.name)
            elif not filter:
                keys.append(key.name)
    logger.info(', '.join(keys))


def help():
    logger.info("List of available commands:")
    for _, info in commands.items():
        logger.info(info["help"])


def give_item(user, item_name, item_type, rarity=Rarity.NONE, amount=1):
    _, userAccount = get_user(nickname=user)
    if not userAccount:
        logger.debug("User is not online")
        return
    item = items.generate_item(ItemEnum[item_name], ItemType[item_type], Rarity[rarity], 4, 0, amount)
    if not item.itemId:
        logger.debug("Error: Item may not be valid")
        return
    it = Item()
    it.character_id = userAccount.character.id
    it.item_id = item.itemId
    it.quantity = item.itemCount
    it.inventory_id = item.inventoryId
    it.slot_id = item.slotId
    it.save()


def list(location=None):
    try:
        _, in_lobby, in_dungeon = count_friends()
    except Exception:
        logger.info("No users currently online.")
        return
    if location == 'lobby':
        logger.info(f"Currently in lobby : {in_lobby}")
    elif location == 'dungeon':
        logger.info(f"Currently in dungeon : {in_dungeon}")
    else:
        logger.info(f"Currently online : {in_lobby + in_dungeon}")


def exit():
    sys.exit(0)


commands = {
    "/help": {"function": help, "help": "/help - Show help"},
    "/give": {"function": give_item, "help": "/give <user> <item_name> <rarity> [amount] - Give someone an item"},
    "/enum": {"function": enum, "help": "/enum items|rarity [filter] - List enums"},
    "/exit": {"function": exit, "help": "/exit - Gracefully exit the server"},
    "/list": {"function": list, "help": "/list [dungeon|lobby] - List players online"}
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
            logger.info("Invalid command. Type /help to get the list of commands")
            continue

        try:
            commands[parts[0]]["function"](*parts[1:])
        except TypeError:
            logger.info(f"Invalid command. Usage: {commands[parts[0]]['help']}")
