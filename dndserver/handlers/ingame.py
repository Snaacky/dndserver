from dndserver.protos import PacketCommand as pc
from dndserver.protos.InGame import (SC2S_AUTO_MATCH_REG_REQ, SS2C_AUTO_MATCH_REG_RES)

def matchmaking(ctx, msg):
    req = SC2S_AUTO_MATCH_REG_REQ()
    req.ParseFromString(msg)
    print(f"Matchmaking: {msg}")
    res = SS2C_AUTO_MATCH_REG_RES(result=pc.SUCCESS)
    return res
