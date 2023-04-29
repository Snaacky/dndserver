from dndserver.database import db

from dndserver.protos import PacketCommand as pc
from dndserver.protos.Inventory import (
    SC2S_INVENTORY_SINGLE_UPDATE_REQ,
    SS2C_INVENTORY_SINGLE_UPDATE_RES,
    SC2S_INVENTORY_MOVE_REQ,
    SS2C_INVENTORY_MOVE_RES,
)
from dndserver.sessions import sessions
from dndserver.models import Character, Item, ItemAttribute


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
    attributes = db.query(ItemAttribute).filter_by(item_id=item.id).all()
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

    # get the current character
    char_query = db.query(Character).filter_by(id=sessions[ctx.transport].character.id).first()

    for old, new in zip(list(req.oldItem), list(req.newItem)):
        # get the current item in the database
        item_query = db.query(Item).filter_by(character_id=char_query.id).filter_by(id=new.itemUniqueId).first()

        # check if we have the item in the database
        if item_query is None:
            return SS2C_INVENTORY_SINGLE_UPDATE_RES(result=pc.FAIL_GENERAL, oldItem=req.oldItem, newItem=req.newItem)

        # handle the move request
        if req.singleUpdateFlag == 0:
            item_query.inventory_id = new.inventoryId
            item_query.slot_id = new.slotId

    return SS2C_INVENTORY_SINGLE_UPDATE_RES(result=pc.SUCCESS, oldItem=req.oldItem, newItem=req.newItem)
