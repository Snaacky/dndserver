from dndserver.database import db
from dndserver.models import Character
from dndserver.protos import PacketCommand as pc
from dndserver.protos.Account import SC2S_LOBBY_ENTER_REQ, SS2C_LOBBY_ENTER_RES
from dndserver.protos.Lobby import (SC2S_CHARACTER_SELECT_ENTER_REQ, SC2S_LOBBY_REGION_SELECT_REQ,
                                    SS2C_LOBBY_REGION_SELECT_RES, SS2C_CHARACTER_SELECT_ENTER_RES,
                                    SC2S_LOBBY_GAME_DIFFICULTY_SELECT_REQ, SS2C_LOBBY_GAME_DIFFICULTY_SELECT_RES,
                                    SS2C_OPEN_LOBBY_MAP_RES, SC2S_OPEN_LOBBY_MAP_REQ)
from dndserver.sessions import sessions


def enter_lobby(ctx, msg):
    """Occurs when loading into the lobby from the character selection screen."""
    req = SC2S_LOBBY_ENTER_REQ()
    req.ParseFromString(msg)
    query = db.query(Character).filter_by(id=req.characterId).first()
    res = SS2C_LOBBY_ENTER_RES(result=pc.SUCCESS, accountId=str(query.user_id))
    sessions[ctx.transport]["character"] = query
    return res


def region_select(ctx, msg):
    """Currently unused."""
    req = SC2S_LOBBY_REGION_SELECT_REQ()
    req.ParseFromString(msg)
    res = SS2C_LOBBY_REGION_SELECT_RES(result=pc.SUCCESS, region=req.region)
    return res


def start(ctx, msg):
    """Currently unused."""
    req = SC2S_CHARACTER_SELECT_ENTER_REQ()
    req.ParseFromString(msg)
    res = SS2C_CHARACTER_SELECT_ENTER_RES(result=pc.SUCCESS)
    return res


def enter_character_select(ctx, msg):
    """Occurs when client enter in the characters selection menu."""
    res = SS2C_CHARACTER_SELECT_ENTER_RES()
    res.result = 1
    return res


def map_select(ctx, msg):
    """Occurs when client selects a map."""
    req = SC2S_LOBBY_GAME_DIFFICULTY_SELECT_REQ()
    req.ParseFromString(msg)
    res = SS2C_LOBBY_GAME_DIFFICULTY_SELECT_RES(result=pc.SUCCESS, gameDifficultyTypeIndex=req.gameDifficultyTypeIndex)
    return res


def open_lobby_map(ctx, msg):
    req = SC2S_OPEN_LOBBY_MAP_REQ()
    req.ParseFromString(msg)
    res = SS2C_OPEN_LOBBY_MAP_RES()
    return res
