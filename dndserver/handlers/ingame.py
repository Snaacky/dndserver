from dndserver.protos import PacketCommand as pc
from dndserver.protos.InGame import (
    SC2S_AUTO_MATCH_REG_REQ, SS2C_AUTO_MATCH_REG_RES,
    SS2C_ENTER_GAME_SERVER_NOT)

from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.sessions import sessions
from dndserver.handlers import character

def matchmaking(ctx, msg):
    req = SC2S_AUTO_MATCH_REG_REQ()
    req.ParseFromString(msg)
    print(f"Matchmaking: {msg}")
    ctx.reply(enter_game_server(ctx, msg))
    res = SS2C_AUTO_MATCH_REG_RES(result=pc.SUCCESS)
    return res

def enter_game_server(ctx, msg):
    character = sessions[ctx.transport].character
    res = SS2C_ENTER_GAME_SERVER_NOT(
        port=7777,
        ip='127.0.0.1',
        accountId=f"{sessions[ctx.transport].account.id}",
        nickName=SACCOUNT_NICKNAME(
            originalNickName=character.nickname,
            streamingModeNickName=character.streaming_nickname
        ),
    )
    return res

def relogin(ctx, msg):
    req = SC2S_RE_LOGIN_REQ()
    req.ParseFromString(msg)
    print(f"Relogging: {msg}")
    ctx.reply(enter_game_server(ctx, msg))
    res = SS2C_RE_LOGIN_RES(address='127.0.0.1', accountId=f"{sessions[ctx.transport].account.id}")
    return res

def floor_matchmaked(ctx, msg):
    res = SS2C_FLOOR_MATCHMAKED_NOT(port=7777, ip='127.0.0.1') 
    return res
