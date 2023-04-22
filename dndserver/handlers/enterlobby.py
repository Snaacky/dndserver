from dndserver.protos import Account_pb2 as acc


def enter_lobby(ctx, data: bytes):
    req = acc.SC2S_LOBBY_ENTER_REQ()
    req.ParseFromString(data[8:])

    res = acc.SS2C_LOBBY_ENTER_RES()
    res.result = 1
    res.accountId = "11"

    return res
