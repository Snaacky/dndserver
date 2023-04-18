from loguru import logger
from twisted.internet.protocol import Factory, Protocol


from dndserver.handlers import login
from dndserver.handlers import character
from dndserver.protos import _PacketCommand_pb2 as pc


class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()


class GameProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()
        self.packet_header= b"\x1e\x00\x00\x00\x0c\x00\x00\x00"
        
        
    def connectionMade(self):
        logger.debug("Connection made")

    def dataReceived(self, data: bytes):
        logger.debug(f"Received {pc.PacketCommand.Name(data[4])}")
        print(f"Received ", data)
        match pc.PacketCommand.Name(data[4]):
            # TODO: Can we access these enums directly? 'EnumTypeWrapper' object is not callable
            case "C2S_ALIVE_REQ":
                logger.debug(data)
                self.transport.write(pc.SS2C_ALIVE_RES().SerializeToString())
                
            case "C2S_ACCOUNT_LOGIN_REQ":
                self.transport.write(login.process_login(self, data))

            case "C2S_ACCOUNT_CHARACTER_CREATE_REQ":

                self.transport.write(character.process_character(self, data))
                logger.debug(f"Received {pc.PacketCommand.Name(data[4])}")
            case _:
                logger.error(f"Received {pc.PacketCommand.Name(data[4])} {data} packet but no handler yet")
