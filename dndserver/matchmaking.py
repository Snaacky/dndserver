import time
from dndserver.persistent import matchmaking_users
from dndserver.protos.InGame import SS2C_FLOOR_MATCHMAKED_NOT, SS2C_ENTER_GAME_SERVER_NOT, SS2C_AUTO_MATCH_REG_TEAM_NOT
from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.utils import make_header
from dndserver.protos.Defines import Define_Game


class Server:
    def __init__(self, ip, port, slots, players):
        self.ip = ip
        self.port = port
        self.slots = slots
        self.players = players


virtualServers = {
    Define_Game.DifficultyType.NORMAL: [
        Server("127.0.0.1", 9999, 18, []),
        Server("127.0.0.1", 10002, 18, []),
        Server("127.0.0.1", 10003, 18, []),
    ],
    Define_Game.DifficultyType.HIGH_ROLLER: [
        Server("127.0.0.1", 9999, 18, []),
        Server("127.0.0.1", 20002, 18, []),
        Server("127.0.0.1", 20003, 18, []),
    ],
    Define_Game.DifficultyType.GOBLIN: [
        Server("127.0.0.1", 9999, 10, []),
        Server("127.0.0.1", 30002, 10, []),
        Server("127.0.0.1", 30003, 10, []),
    ],
    Define_Game.DifficultyType.RUINS: [
        Server("127.0.0.1", 9999, 18, []),
        Server("127.0.0.1", 40002, 18, []),
        Server("127.0.0.1", 40003, 18, []),
    ],
}


def matchmaking():
    for usertuple in matchmaking_users:
        transport = usertuple[0]
        user = usertuple[1]
        req = usertuple[2]
        availableServer = list(filter(lambda x: len(x.players) < x.slots, virtualServers[req.difficultyType]))[0]
        if not availableServer:
            print("Couldn't find a server for the user. Retrying later...")
            time.sleep(1)
            matchmaking()
        availableServer.players.append(user)
        match = SS2C_FLOOR_MATCHMAKED_NOT(
            port=availableServer.port, ip=availableServer.ip, sessionId=str(user.account.id)
        )
        header = make_header(match)
        transport.write(header + match.SerializeToString())
        res = SS2C_ENTER_GAME_SERVER_NOT(
            port=availableServer.port,
            ip=availableServer.ip,
            sessionId=str(user.account.id),
            accountId=str(user.account.id),
            isReconnect=0,
            nickName=SACCOUNT_NICKNAME(
                originalNickName=user.character.nickname, streamingModeNickName=user.character.streaming_nickname
            ),
        )
        header = make_header(res)
        transport.write(header + res.SerializeToString())
        print("found a server for user :", availableServer.__dict__)
        matchmaking_users.remove(usertuple)
