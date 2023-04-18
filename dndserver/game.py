from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver import database
from dndserver.handlers import login
from dndserver.handlers import character
from dndserver.protos import _PacketCommand_pb2 as pc


class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()


class GameProtocol(Protocol):
    def connectionMade(self):
        logger.debug("Connection made")

    def dataReceived(self, data: bytes):
        logger.debug(f"Received {pc.PacketCommand.Name(data[4])}")
        match pc.PacketCommand.Name(data[4]):
            # TODO: Can we access these enums directly? 'EnumTypeWrapper' object is not callable
            case "C2S_ALIVE_REQ":
                self.send(pc.SS2C_ALIVE_RES().SerializeToString())
            case "C2S_ACCOUNT_LOGIN_REQ":
                self.send(login.process_login(self, data))
            case "C2S_ACCOUNT_CHARACTER_LIST_REQ":
                self.send(character.list_characters(self, data))
            case "C2S_ACCOUNT_CHARACTER_CREATE_REQ":
                self.send(character.create_character(self, data))
            case _:
                logger.error(f"Received {pc.PacketCommand.Name(data[4])} {data} packet but no handler yet")

    def send(self, data: bytes):
        self.transport.write(data)

    def send_many(self, packets: list):
        for packet in packets:
            self.transport.write(packet)
