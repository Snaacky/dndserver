from dndserver.protos import Lobby_pb2 as lb


def startgame(ctx, data: bytes):
    req = lb.SC2S_CHARACTER_SELECT_ENTER_REQ()
    req.ParseFromString(data[8:])
    print(req)
    res = lb.SS2C_CHARACTER_SELECT_ENTER_RES()
    res.result = 1
    return res
