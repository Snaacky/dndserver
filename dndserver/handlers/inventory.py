from dndserver.database import db
from dndserver.models import Character, Item, ItemAttribute
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Inventory import (
    SC2S_INVENTORY_MOVE_REQ,
    SC2S_INVENTORY_SINGLE_UPDATE_REQ,
    SS2C_INVENTORY_MOVE_RES,
    SS2C_INVENTORY_SINGLE_UPDATE_RES,
)


def get_all_items(character_id):
    """Helper function to get all items for a character id"""
    query = db.query(Item).filter_by(character_id=character_id)
    ret = list()

    for item in query:
        # add the attributes of the item
        attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()

        # add the attributes and the item
        ret.append((item, attributes))

    return ret


def delete_item(character_id, item):
    """Helper function to remove a item from a character"""
    query = db.query(Item).filter_by(character_id=character_id).filter_by(id=item.itemUniqueId).first()

    # check if we have the item
    if query is None:
        return False

    # delete all the attributes the item has
    attributes = db.query(ItemAttribute).filter_by(item_id=item.itemId).all()
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
    if "Id_Item_Bandage" in item or "Potion" in item:
        return 3
    elif "Id_Item_GoldCoinPurse" in item or "Id_Item_GoldCoinChest" in item or "Id_Item_GoldCoinBag" in item:
        return 1
    elif "Id_Item_GoldCoins" or "Id_Item_SilverCoin" in item:
        return 10
    else:
        return 0


def get_inv_limit(item):
    # TODO: get real values for limits
    if "Id_Item_GoldCoinPurse" in item:
        return 50
    elif "Id_Item_GoldCoinBag" in item:
        return 200
    elif "Id_Item_GoldCoinChest" in item:
        return 1000
    else:
        return 0


def move_item(ctx, msg):
    """Occurs when the user moves an item at a merchant"""
    req = SC2S_INVENTORY_MOVE_REQ()
    req.ParseFromString(msg)

    # get the current character
    char_query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()

    # get the current item in the database
    item_query = db.query(Item).filter_by(character_id=char_query.id).filter_by(id=req.srcInfo.uniqueId).first()

    if item_query is not None:
        item_query.inventory_id = req.dstInventoryId
        item_query.slot_id = req.dstSlotId

    return SS2C_INVENTORY_MOVE_RES()


def move_single_item(ctx, msg):
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
        old_query = db.query(Item).filter_by(character_id=character.id).filter_by(id=old.itemUniqueId).first()

        # check if we have the item in the database
        if old_query is None:
            continue

        # check for a simple move
        if old.itemUniqueId == new.itemUniqueId:
            # we have a simple move move request, handle it
            old_query.inventory_id = new.inventoryId
            old_query.slot_id = new.slotId

            continue

        # Not a simple move, search for the item we are updating to
        new_query = db.query(Item).filter_by(character_id=character.id).filter_by(id=new.itemUniqueId).first()

        # check if we have both items in the database
        if new_query is None:
            it = Item()
            it.character_id = old_query.character_id
            it.quantity = new.itemCount
            it.inventory_id = new.inventoryId
            it.slot_id = new.slotId

            attributes = list()

            if get_inv_limit(old.itemId):
                # move item out of purse. decrease the amount of items in the inventory. The amount
                # of items we need to remove is stored in the item count
                old_query.inv_count -= new.itemCount

                # extract the item out of the inventory
                it.item_id = new.itemId

            else:
                # The new item is not in the database. This means it has split. decrement the old item
                old_query.quantity -= old.itemCount

                # create a new item in the database
                it.item_id = old.itemId

                # copy all the attributes
                item_attr = db.query(ItemAttribute).filter_by(item_id=old.itemUniqueId).all()
                for attribute in item_attr:
                    attr = ItemAttribute()
                    attr.item_id = attribute.item_id
                    attr.primary = attribute.primary
                    attr.property = attribute.property
                    attr.value = attribute.value

                    attributes.append(attr)

            # add the item ot the database
            add_item((it, attributes))

            # update the unique id to notify the client what id to use
            new.itemUniqueId = it.id

        else:
            # check what action to do
            if get_inv_limit(old.itemId) and get_inv_limit(new.itemId):
                # move item from one purse to another
                total_count = new_query.inv_count + new.itemContentsCount
                inventory_limit = get_inv_limit(new.itemId)

                # limit the amount of items in the inventory
                if total_count > inventory_limit:
                    # we have a overflow. Increase the amount on the new item till it does not fit anymore
                    old_query.inv_count = total_count - inventory_limit
                    new_query.inv_count = inventory_limit
                else:
                    old_query.inv_count = 0
                    new_query.inv_count = total_count

            elif get_inv_limit(new.itemId):
                # move item into purse. Put the item in the inventory and delete the other one if everything fits
                total_count = new_query.inv_count + old.itemCount
                inventory_limit = get_inv_limit(new.itemId)

                # limit the amount of items in the inventory
                if total_count > inventory_limit:
                    # we have a overflow. Keep the old item and decrease it. Increase the amount on the new item
                    old_query.quantity = total_count - inventory_limit
                    new_query.inv_count = inventory_limit

                else:
                    new_query.inv_count = total_count

                    # delete the item
                    delete_item(character.id, old)

            elif get_stack_limit(new.itemId):
                # we have both items. Merge them
                total_count = old.itemCount + new.itemCount
                stack_limit = get_stack_limit(new.itemId)

                # limit the amount of items in a stack. The game expects this and wont update otherwise
                if total_count > stack_limit:
                    # we have a overflow. Keep the old item and decrease it. Increase the amount on the new item
                    old_query.quantity = total_count - stack_limit
                    new_query.quantity = stack_limit

                else:
                    # Everything fits in the new item. Merge and delete the old item
                    new_query.quantity = total_count

                    # delete the item
                    delete_item(character.id, old)

            else:
                # return a error as we cannot process this request
                return SS2C_INVENTORY_SINGLE_UPDATE_RES(
                    result=pc.FAIL_NO_VALUE, oldItem=req.oldItem, newItem=req.newItem
                )

    return SS2C_INVENTORY_SINGLE_UPDATE_RES(result=pc.SUCCESS, oldItem=req.oldItem, newItem=req.newItem)
