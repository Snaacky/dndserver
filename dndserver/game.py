from loguru import logger
from twisted.internet.protocol import Factory, Protocol


from dndserver.handlers import login
from dndserver.protos import _PacketCommand_pb2 as pc


class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()


class GameProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()
        self.packet_header = b"\x1e\x00\x00\x00\x0c\x00\x00\x00"

    def connectionMade(self):
        logger.debug("Connection made")

    def dataReceived(self, data: bytes):
        logger.debug(f"Received {pc.PacketCommand.Name(data[4])}")
        match pc.PacketCommand.Name(data[4]):
            # TODO: Can we access these enums directly? 'EnumTypeWrapper' object is not callable
            case "C2S_ALIVE_REQ":
                logger.debug(data)
                self.respond(pc.SS2C_ALIVE_RES().SerializeToString())
            case "C2S_ACCOUNT_LOGIN_REQ":
                self.respond(login.process_login(self, data))
            case _:
                logger.error(f"Received {pc.PacketCommand.Name(data[4])} {data} packet but no handler yet")

    def respond(self, data):
        """Wrapper that adds the packet header onto the serialized data blob"""
        self.transport.write(self.packet_header + data)
