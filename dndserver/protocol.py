from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver.handlers import character, lobby, login
from dndserver.protos import Account_pb2 as acc, _Defins_pb2 as df, _PacketCommand_pb2 as pc, Lobby_pb2 as lby


class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()


class GameProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()
        # Where all of the game server related connection session
        # data is stored.
        self.sessions = {}

    def connectionMade(self):
        """Event for when a client connects to the server."""
        logger.debug("Connection made")
        self.sessions[self.transport] = {"accountId": 0}

    def dataReceived(self, data: bytes):
        """Main loop for receiving request packets and sending response packets."""
        # Manually catch and skip any unparsed packets
        try:
            logger.debug(f"Received {pc.PacketCommand.Name(data[4])}")
        except ValueError:
            return logger.error(f"Received {data[4]} {data} packet but no handler yet")

        # TODO: Surely there's a cleaner way that we can do this?
        # TODO: Can we access these enums directly? 'EnumTypeWrapper' object is not callable
        match pc.PacketCommand.Name(data[4]):

            # Heartbeat sent between the client and server every second.
            case "C2S_ALIVE_REQ":
                self.transport.write(pc.SS2C_ALIVE_RES().SerializeToString())

            # Login attempt from the client.
            case "C2S_ACCOUNT_LOGIN_REQ":
                req = acc.SC2S_ACCOUNT_LOGIN_REQ()
                req.ParseFromString(data[8:])
                res = login.process_login(self, req).SerializeToString()
                header = self.make_header(res, "S2C_ACCOUNT_LOGIN_RES")
                self.sessions[self.transport]["state"] = df.Define_Common.CHARACTER_SELECT
                self.send(header, res)

            # Sends character list to the character screen and sends character information
            # when in the lobby/tavern.
            case "C2S_ACCOUNT_CHARACTER_LIST_REQ":
                if self.sessions[self.transport]["state"] == df.Define_Common.CHARACTER_SELECT:
                    req = acc.SC2S_ACCOUNT_CHARACTER_LIST_REQ()
                    req.ParseFromString(data[8:])
                    res = character.list_characters(self, req).SerializeToString()
                    header = self.make_header(res, "S2C_ACCOUNT_CHARACTER_LIST_RES")
                    self.send(header, res)
                elif self.sessions[self.transport]["state"] == df.Define_Common.PLAY:
                    res = character.character_info(self).SerializeToString()
                    header = self.make_header(res, "S2C_LOBBY_CHARACTER_INFO_RES")
                    self.send(header, res)

            # Character creation attempt from the client.
            case "C2S_ACCOUNT_CHARACTER_CREATE_REQ":
                req = acc.SC2S_ACCOUNT_CHARACTER_CREATE_REQ()
                req.ParseFromString(data[8:])
                res = character.create_character(self, req).SerializeToString()
                header = self.make_header(res, "S2C_ACCOUNT_CHARACTER_CREATE_RES")
                self.send(header, res)

            # Character deletion attempt from the client.
            case "C2S_ACCOUNT_CHARACTER_DELETE_REQ":
                req = acc.SC2S_ACCOUNT_CHARACTER_DELETE_REQ()
                req.ParseFromString(data[8:])
                res = character.delete_character(self, req).SerializeToString()
                header = self.make_header(res, "S2C_ACCOUNT_CHARACTER_DELETE_RES")
                self.send(header, res)

            # Client attempting to load into the lobby.
            case "C2S_LOBBY_ENTER_REQ":
                req = acc.SC2S_LOBBY_ENTER_REQ()
                req.ParseFromString(data[8:])
                res = lobby.enter_lobby(req).SerializeToString()
                header = self.make_header(res, "S2C_LOBBY_ENTER_RES")
                self.send(header, res)
                self.sessions[self.transport]["state"] = df.Define_Common.PLAY

            case "C2S_LOBBY_REGION_SELECT_REQ":
                if self.sessions[self.transport]["state"] == df.Define_Common.PLAY and len(data) == 10:
                    req = lby.SC2S_LOBBY_REGION_SELECT_REQ()
                    req.ParseFromString(data[8:])
                    res = lobby.region_select(self, req).SerializeToString()
                    header = self.make_header(res, "S2C_LOBBY_REGION_SELECT_RES")
                    self.send(header, res)
                elif self.sessions[self.transport]["state"] == df.Define_Common.CHARACTER_SELECT:
                    pass
            case "C2S_LOBBY_GAME_DIFFICULTY_SELECT_REQ":
                req = lby.SC2S_LOBBY_GAME_DIFFICULTY_SELECT_REQ()
                req.ParseFromString(data[8:])

                res = lby.SS2C_LOBBY_GAME_DIFFICULTY_SELECT_RES()
                res.result = 1
                res.gameDifficultyTypeIndex = req.gameDifficultyTypeIndex
                res = res.SerializeToString()

                header = self.make_header(res, "S2C_LOBBY_GAME_DIFFICULTY_SELECT_RES")
                self.send(header, res)
            case "C2S_CHARACTER_SELECT_ENTER_REQ":
                res = lby.SS2C_CHARACTER_SELECT_ENTER_RES()
                res.result = 1
                res = res.SerializeToString()
                header = self.make_header(res, "S2C_CHARACTER_SELECT_ENTER_RES")
                self.send(header, res)
                self.sessions[self.transport]["state"] = df.Define_Common.CHARACTER_SELECT

            # All other currently unhandled packets.
            case _:
                logger.error(f"Received {pc.PacketCommand.Name(data[4])} {data} packet but no handler yet")

    def send(self, header: bytes, body: bytes):
        """Send a D&D packet to the client."""
        self.transport.write(header + body)

    def connectionLost(self, reason):
        """Event for when a client disconnects from the server."""
        return NotImplementedError

    def make_header(self, res: bytes, packet_id: str):
        """Create a D&D packet header."""
        # header: <packet length> 00 00 <packet id> 00 00
        if not res:
            raise Exception("Didn't pass data when creating header")
        type_ = pc.PacketCommand.Value(packet_id).to_bytes(2, "little")
        length_ = (len(res) + 8).to_bytes(2, "little")
        return length_ + b"\x00\x00" + type_ + b"\x00\x00"
