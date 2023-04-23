from dndserver import database
from dndserver.protos import Account_pb2 as acc
from dndserver.protos import Lobby_pb2 as lb


def enter_lobby(req):
    """Communication that occurs when loading into the lobby from the
    character selection screen."""
    res = acc.SS2C_LOBBY_ENTER_RES()
    res.result = 1
    db = database.get()
    result = db["characters"].find_one(id=req.characterId)
    res.accountId = str(result["owner_id"])
    return res


def character_select(req):
    res = lb.SS2C_CHARACTER_SELECT_ENTER_RES()
    res.result = 1

    return res


def region_select(ctx, req):
    """Currently unused."""
    # req = lb.SC2S_LOBBY_REGION_SELECT_REQ()
    # req.ParseFromString(data[8:])
    res = lb.SS2C_LOBBY_REGION_SELECT_RES()
    res.result = 1
    res.region = req.region
    return res


def start(ctx, req):
    """Currently unused."""
    # req = lb.SC2S_CHARACTER_SELECT_ENTER_REQ()
    # req.ParseFromString(data[8:])
    res = lb.SS2C_CHARACTER_SELECT_ENTER_RES()
    res.result = 1
    return res
