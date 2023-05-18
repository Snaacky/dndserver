import time
from dndserver.persistent import matchmaking_users
from dndserver.protos.InGame import SS2C_FLOOR_MATCHMAKED_NOT, SS2C_ENTER_GAME_SERVER_NOT, SS2C_AUTO_MATCH_REG_TEAM_NOT
from dndserver.protos.Character import SACCOUNT_NICKNAME
from dndserver.utils import make_header
from dndserver.protos.Defines import Define_Game
from dndserver.utils import get_user, make_header


class Server:
    def __init__(self, ip, port, slots, players):
        self.ip = ip
        self.port = port
        self.slots = slots
        self.players = players


virtualServers = {
    Define_Game.DifficultyType.NORMAL: [
        Server("127.0.0.1", 7777, 10, []),
        Server("127.0.0.1", 10002, 10, []),
        Server("127.0.0.1", 10003, 10, []),
    ],
    Define_Game.DifficultyType.HIGH_ROLLER: [
        Server("127.0.0.1", 7777, 10, []),
        Server("127.0.0.1", 20002, 10, []),
        Server("127.0.0.1", 20003, 10, []),
    ],
    Define_Game.DifficultyType.GOBLIN: [
        Server("127.0.0.1", 7777, 10, []),
        Server("127.0.0.1", 30002, 10, []),
        Server("127.0.0.1", 30003, 10, []),
    ],
    Define_Game.DifficultyType.RUINS: [
        Server("127.0.0.1", 7777, 10, []),
        Server("127.0.0.1", 40002, 10, []),
        Server("127.0.0.1", 40003, 10, []),
    ],
}


def get_available_server(party):
    playerCount = len(party["party"].players)
    availableServers = list(
        filter(lambda x: len(x.players) + playerCount <= x.slots, virtualServers[party["difficulty"]])
    )
    if len(availableServers) > 0:
        return availableServers[0]
    else:
        return None


def matchmaking():
    while True:
        time.sleep(2)
        for party in matchmaking_users:
            server = get_available_server(party)
            if server is None:
                print("Server not found. Searching...")
                continue
            # We have found a server for the party. Now we need to notify them.
            for player in party["party"].players:
                transport, _ = get_user(account_id=player.account.id)
                match = SS2C_FLOOR_MATCHMAKED_NOT(port=server.port, ip=server.ip, sessionId=str(player.account.id))
                header = make_header(match)
                transport.write(header + match.SerializeToString())
                res = SS2C_ENTER_GAME_SERVER_NOT(
                    port=server.port,
                    ip=server.ip,
                    sessionId=str(player.account.id),
                    accountId=str(player.account.id),
                    isReconnect=0,
                    nickName=SACCOUNT_NICKNAME(
                        originalNickName=player.character.nickname,
                        streamingModeNickName=player.character.streaming_nickname,
                    ),
                )
                header = make_header(res)
                transport.write(header + res.SerializeToString())
                server.players.append(player)
            matchmaking_users.remove(party)
