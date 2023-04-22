from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver.handlers import login
from dndserver.protos import _PacketCommand_pb2 as pc

# Factory class that creates GameProtocol instances
class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()

# Protocol class for handling game connections
class GameProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()
        # Packet header used for sending responses
        self.packet_header = b"\x1e\x00\x00\x00\x0c\x00\x00\x00"

    def connectionMade(self):
        # Log when a new connection is made
        logger.debug("Connection made")

    def dataReceived(self, data: bytes):
        # Log the received packet command
        logger.debug(f"Received {pc.PacketCommand.Name(data[4])}")

        # Handle different packet commands
        match pc.PacketCommand.Name(data[4]):
            case "C2S_ALIVE_REQ":
                logger.debug(data)
                self.respond(pc.SS2C_ALIVE_RES().SerializeToString())
            case "C2S_ACCOUNT_LOGIN_REQ":
                # Process login and store the result in a variable
                login_result = login.process_login(self, data)
                # Log the result
                print("Login result:", login_result)
                # Pass the result to the respond function
                self.respond(login_result)
            case _:
                logger.error(f"Received {pc.PacketCommand.Name(data[4])} {data} packet but no handler yet")

    def respond(self, data):
        """
        Wrapper that adds the packet header onto the serialized data blob
        and sends the response to the client.
        """
        self.transport.write(self.packet_header + data)
