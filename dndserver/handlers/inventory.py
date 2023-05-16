from dndserver.database import db
from dndserver.models import Character, Item, ItemAttribute
from dndserver.persistent import sessions
from dndserver.handlers import character as HCharacter
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Inventory import (
    SC2S_INVENTORY_MOVE_REQ,
    SC2S_INVENTORY_SINGLE_UPDATE_REQ,
    SS2C_INVENTORY_MOVE_RES,
    SS2C_INVENTORY_SINGLE_UPDATE_RES,
    SC2S_INVENTORY_MERGE_REQ,
    SC2S_INVENTORY_SPLIT_MOVE_REQ,
    SC2S_INVENTORY_SWAP_REQ,
    SC2S_INVENTORY_SPLIT_MERGE_REQ,
    SS2C_INVENTORY_MERGE_RES,
    SS2C_INVENTORY_SPLIT_MOVE_RES,
    SS2C_INVENTORY_SWAP_RES,
    SS2C_INVENTORY_SPLIT_MERGE_RES,
)


def get_all_items(character_id, inventory_id=None, slot_id=None):
    """Helper function to get all items for a character id"""
    query = db.query(Item).filter_by(character_id=character_id).filter_by(index=0)

    if inventory_id is not None:
        query = query.filter_by(inventory_id=inventory_id)

    if slot_id is not None:
        query = query.filter_by(slot_id=slot_id)

    ret = list()

    for item in query:
        # add the attributes of the item
        attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()

        # add the attributes and the item
        ret.append((item, attributes))

    return ret


def delete_item(character_id, item, is_query=False):
    """Helper function to remove a item from a character"""
    if is_query:
        query = item
    else:
        query = db.query(Item).filter_by(character_id=character_id).filter_by(id=item.itemUniqueId).first()

    # check if we have the item
    if query is None:
        return False

    # delete all the attributes the item has
    attributes = db.query(ItemAttribute).filter_by(item_id=query.id).all()
    for attribute in attributes:
        attribute.delete()

    # delete the item
    query.delete()

    return True


def add_item(item):
    """Helper function to add a item to a character"""
    it, attributes = item

    # store the item
    it.save()

    for attribute in attributes:
        attribute.save()


def get_stack_limit(item):
    """Helper function to the get the amount we can stack a item"""
    # TODO: this should be read from the item directly
    if "Id_Item_Bandage" in item or "Potion" in item or "Id_Item_ThrowingKnife" in item:
        return 3
    elif "Id_Item_GoldCoinPurse" in item or "Id_Item_GoldCoinChest" in item or "Id_Item_GoldCoinBag" in item:
        return 1
    elif "Id_Item_GoldCoins" in item or "Id_Item_SilverCoin" in item:
        return 10
    elif "Id_Item_Arrow" in item:
        return 15
    else:
        return 0


def get_inv_limit(item):
    """Helper function to get the max inventory count for a item"""
    # TODO: get real values for limits
    if "Id_Item_GoldCoinPurse" in item:
        return 50
    elif "Id_Item_GoldCoinBag" in item:
        return 200
    elif "Id_Item_GoldCoinChest" in item:
        return 1000
    else:
        return 0


def split_item(from_item, item_id, to_inventory, to_slot, quantity, character_id, from_is_persistent=True):
    """Helper function to split a item and generate a new item at the provided location"""
    it = Item()
    it.character_id = character_id
    it.inventory_id = to_inventory
    it.slot_id = to_slot
    it.quantity = quantity
    attributes = list()

    # check how we should split the item
    if get_inv_limit(from_item.item_id):
        # move item out of purse. decrease the amount of items in the inventory. The amount
        # of items we need to remove is stored in the item count
        from_item.inv_count -= quantity

        # extract the item out of the inventory
        it.item_id = item_id

    else:
        # The new item is not in the database. This means it has split. decrement the old item
        from_item.quantity -= quantity

        # create a new item in the database
        it.item_id = from_item.item_id

        # copy all the attributes
        item_attr = db.query(ItemAttribute).filter_by(item_id=from_item.id).all()
        for attribute in item_attr:
            attr = ItemAttribute()
            attr.item_id = attribute.item_id
            attr.primary = attribute.primary
            attr.property = attribute.property
            attr.value = attribute.value
            attributes.append(attr)

    # add the item ot the database
    add_item((it, attributes))

    # check if we should delete the old item. This only happens when the game is confused and
    # tries a split on a item that is not stacked
    if from_item.quantity <= 0 and from_is_persistent:
        delete_item(character_id, from_item, True)

    # update the unique id to notify the client what id to use
    return it.id


def merge_items(from_item, to_item, amount, character_id, from_is_persistent=True):
    """Helper function to merge two items."""
    # Check how we can merge the two items
    if get_inv_limit(from_item.item_id) and get_inv_limit(to_item.item_id):
        # we have two items that have a inventory. Merge the to items together by
        # moving the inventory from one to the other
        limit = get_inv_limit(to_item.item_id)
        total = to_item.inv_count + amount

        # move the inventory of the target until the limit
        to_item.inv_count = min(total, limit)
        from_item.inv_count -= amount if total <= limit else total - limit

        # do a early return as we should not delete the item we moved from
        return True

    elif get_inv_limit(to_item.item_id):
        # the target is a item with a inventory. Move the quantity into the target
        limit = get_inv_limit(to_item.item_id)
        total = to_item.inv_count + amount

        # move the quantity to the target until the limit
        to_item.inv_count = min(total, limit)
        from_item.quantity -= amount if total <= limit else total - limit

    elif get_stack_limit(to_item.item_id):
        # the target is a item that can hold a stack. Move the item(s) to the target
        limit = get_stack_limit(to_item.item_id)
        total = to_item.quantity + amount

        # move the items in the stack
        to_item.quantity = min(total, limit)
        from_item.quantity -= amount if total <= limit else total - limit

    else:
        # we cannot merge the two items. Return invalid
        return False

    # check if we should delete the old item
    if from_item.quantity <= 0 and from_is_persistent:
        delete_item(character_id, from_item, True)

    return True


def merge_request(ctx, msg):
    """Occurs when the user drags an item on another in the merchant screen."""
    req = SC2S_INVENTORY_MERGE_REQ()
    req.ParseFromString(msg)

    # get the character
    character = sessions[ctx.transport].character

    # get both items we want to merge
    old = db.query(Item).filter_by(character_id=character.id).filter_by(id=req.srcInfo.uniqueId).first()
    new = db.query(Item).filter_by(character_id=character.id).filter_by(id=req.dstInfo.uniqueId).first()

    # get the amount we want to merge
    amount = old.inv_count if old.inv_count > 0 else old.quantity

    # merge the items
    merge_items(old, new, amount, character.id)

    ctx.reply(SS2C_INVENTORY_MERGE_RES())

    return HCharacter.character_info(ctx, bytearray())


def split_move_request(ctx, msg):
    """Occurs when the user wants to split an item in the merchant screen."""
    req = SC2S_INVENTORY_SPLIT_MOVE_REQ()
    req.ParseFromString(msg)

    # get both items we want to merge
    item = (
        db.query(Item)
        .filter_by(character_id=sessions[ctx.transport].character.id)
        .filter_by(id=req.srcInfo.uniqueId)
        .first()
    )

    res = SS2C_INVENTORY_SPLIT_MOVE_RES()

    # special case for the items with a inventory
    if get_inv_limit(item.item_id):
        # for items with a inventory split into gold coins
        res.newUniqueId = split_item(
            item,
            "DesignDataItem:Id_Item_GoldCoins",
            req.dstInventoryId,
            req.dstSlotId,
            req.count,
            sessions[ctx.transport].character.id,
        )
    else:
        res.newUniqueId = split_item(
            item, item.item_id, req.dstInventoryId, req.dstSlotId, req.count, sessions[ctx.transport].character.id
        )
    res.newInventoryId = req.dstInventoryId
    res.newSlotId = req.dstSlotId

    ctx.reply(res)

    return HCharacter.character_info(ctx, bytearray())


def swap_request(ctx, msg):
    """Occurs when the user wants to swap two items in the merchant screen."""
    req = SC2S_INVENTORY_SWAP_REQ()
    req.ParseFromString(msg)

    # get the character
    character = sessions[ctx.transport].character

    # move the main item to the new location
    it = db.query(Item).filter_by(character_id=character.id).filter_by(id=req.srcInfo.uniqueId).first()
    it.inventory_id = req.dstInfo.inventoryId
    it.slot_id = req.dstInfo.slotId

    # move all the other items
    for item in req.swapInfos:
        it = db.query(Item).filter_by(character_id=character.id).filter_by(id=item.dstInfo.uniqueId).first()
        it.inventory_id = item.newInventoryId
        it.slot_id = item.newSlotId

    ctx.reply(SS2C_INVENTORY_SWAP_RES())

    return HCharacter.character_info(ctx, bytearray())


def split_merge_request(ctx, msg):
    """Occurs when the user wants to split and merge the result on another item in the merchant screen."""
    req = SC2S_INVENTORY_SPLIT_MERGE_REQ()
    req.ParseFromString(msg)

    # get the character
    character = sessions[ctx.transport].character

    # get the item we want to split from and the item we want to merge to
    old = db.query(Item).filter_by(character_id=character.id).filter_by(id=req.srcInfo.uniqueId).first()
    new = db.query(Item).filter_by(character_id=character.id).filter_by(id=req.dstInfo.uniqueId).first()

    # create a temporary item with the paramerers for the merge. No need to do both a full split and a merge
    it = Item()
    it.item_id = old.item_id
    it.ammo_count = old.ammo_count

    # check if the item is a inventory item
    if get_inv_limit(it.item_id):
        it.inv_count = req.count
    else:
        it.quantity = req.count

    # merge the two items.
    if merge_items(it, new, req.count, character.id, False):
        # remove the item if successfull
        if get_inv_limit(it.item_id):
            old.inv_count -= req.count
        else:
            old.quantity -= req.count

    ctx.reply(SS2C_INVENTORY_SPLIT_MERGE_RES())

    return HCharacter.character_info(ctx, bytearray())


def move_request(ctx, msg):
    """Occurs when the user moves an item at a merchant"""
    req = SC2S_INVENTORY_MOVE_REQ()
    req.ParseFromString(msg)

    # get the current character
    char_query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()

    # get the current item in the database
    item_query = (
        db.query(Item)
        .filter_by(character_id=char_query.id)
        .filter_by(id=req.srcInfo.uniqueId)
        .filter_by(index=0)
        .first()
    )

    if item_query is not None:
        item_query.inventory_id = req.dstInventoryId
        item_query.slot_id = req.dstSlotId

    ctx.reply(SS2C_INVENTORY_MOVE_RES())

    return HCharacter.character_info(ctx, bytearray())


def move_single_request(ctx, msg):
    """Occurs when the user moves an item in the stash (only in the stash screen)"""
    req = SC2S_INVENTORY_SINGLE_UPDATE_REQ()
    req.ParseFromString(msg)

    if req.singleUpdateFlag != 0:
        # for now only 0 is supported (handles all the moving in the inventory)
        return SS2C_INVENTORY_SINGLE_UPDATE_RES(result=pc.SUCCESS, oldItem=req.oldItem, newItem=req.newItem)

    # get the character
    character = sessions[ctx.transport].character

    for old, new in zip(list(req.oldItem), list(req.newItem)):
        # get the current item in the database
        old_query = (
            db.query(Item)
            .filter_by(character_id=character.id)
            .filter_by(id=old.itemUniqueId)
            .filter_by(item_id=old.itemId)
            .filter_by(index=0)
            .first()
        )

        # check if we have the item in the database
        if old_query is None:
            continue

        # check for a simple move where we do not need to merge/split
        if old.itemUniqueId == new.itemUniqueId:
            # we have a simple move move request, handle it
            old_query.inventory_id = new.inventoryId
            old_query.slot_id = new.slotId

            continue

        # search for the new item in the database. For some reason the game buggs out sometimes and
        # reports the wrong itemId for the item. Do not include it in the search parameters
        new_query = (
            db.query(Item)
            .filter_by(character_id=character.id)
            .filter_by(id=new.itemUniqueId)
            .filter_by(index=0)
            .filter_by(slot_id=new.slotId)
            .filter_by(inventory_id=new.inventoryId)
            .first()
        )

        # check if we have both items in the database
        if new_query is None:
            # We do not have the new item. Split the old item into the new item.
            # Set unique id of the new item
            new.itemUniqueId = split_item(
                old_query, new.itemId, new.inventoryId, new.slotId, new.itemCount, character.id
            )
        else:
            # get the amount we want to merge
            amount = new.itemContentsCount if new.itemContentsCount > 0 else new.itemCount

            # we have a merge
            if merge_items(old_query, new_query, amount, character.id) is False:
                # return a error as we cannot process this request
                return SS2C_INVENTORY_SINGLE_UPDATE_RES(
                    result=pc.FAIL_NO_VALUE, oldItem=req.oldItem, newItem=req.newItem
                )

    ctx.reply(SS2C_INVENTORY_SINGLE_UPDATE_RES(result=pc.SUCCESS, oldItem=req.oldItem, newItem=req.newItem))

    return HCharacter.character_info(ctx, bytearray())
