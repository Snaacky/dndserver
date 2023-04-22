from dndserver.protos import Lobby_pb2 as lb


def region_select(ctx, data: bytes):
    req = lb.SC2S_LOBBY_REGION_SELECT_REQ()
    req.ParseFromString(data[8:])

    res = lb.SS2C_LOBBY_REGION_SELECT_RES()
    res.result = 1
    res.region = req.region

    return res
