from loguru import logger
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

from dndserver.handlers import login
from dndserver.protos import _PacketCommand_pb2 as pc
from collections import defaultdict

# Factory class that creates GameProtocol instances
class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()

# Protocol class for handling game connections
class GameProtocol(Protocol):
    TIMEOUT = 15  # Set your desired timeout value here
    
    def on_timeout(self, client_addr):
        """
        This method is called when the timeout occurs for a client.
        You can perform any cleanup or logging tasks here.
        """
        logger.warning(f"Timeout occurred for client {client_addr}")
        # Remove the timeout entry for the client
        if client_addr in self.timeouts:
            del self.timeouts[client_addr]
        # Remove the partial packet buffer for the client
        if client_addr in self.partial_packets:
            del self.partial_packets[client_addr]

    def __init__(self) -> None:
        super().__init__()
        # Packet header used for sending responses
        self.packet_header = b"\x1e\x00\x00\x00\x0c\x00\x00\x00"
        # Buffer to store partial packets, using client addresses as keys
        self.partial_packets = defaultdict(bytearray)
        # Dictionary to store timeouts for each client
        self.timeouts = {}

    def check_partial_packet(self, client_addr):
        if not self.is_complete_packet(self.partial_packets[client_addr]):
            logger.warning(f"Partial packet from {client_addr} discarded due to timeout")
            self.partial_packets[client_addr] = bytearray()

    def dataReceived(self, data: bytes):
        # Get the address of the client who sent the data
        client_addr = self.transport.getPeer()
        # Log the received data with the client's address
        logger.debug(f"Received data from {client_addr}: {data}")

        # Append the received data to the corresponding buffer
        self.partial_packets[client_addr] += data

        # Schedule a check for partial packets after the timeout
        reactor.callLater(self.TIMEOUT, self.check_partial_packet, client_addr)

        # Keep checking and processing complete packets
        while self.is_complete_packet(self.partial_packets[client_addr]):
            # Extract the full packet
            full_packet, remaining_data = self.extract_packet(self.partial_packets[client_addr])
            # Update the buffer with the remaining data
            self.partial_packets[client_addr] = remaining_data

            # Process the full packet
            self.process_packet(full_packet)

        # If there is still a partial packet left, set a new timeout
        if self.partial_packets[client_addr]:
            self.timeouts[client_addr] = reactor.callLater(self.TIMEOUT, self.on_timeout, client_addr)

    def is_complete_packet(self, data: bytes) -> bool:
        # Return False if the data is not enough to determine the packet length
        if len(data) < 4:
            return False

        # Assuming the first 4 bytes contain the packet length
        packet_length = int.from_bytes(data[:4], byteorder='little')
        return len(data) >= packet_length

    def extract_packet(self, data: bytes) -> tuple[bytes, bytes]:
        # Get the packet length from the first 4 bytes
        packet_length = int.from_bytes(data[:4], byteorder='little')
        # Return the full packet and the remaining data
        return data[:packet_length], data[packet_length:]

    def process_packet(self, data: bytes):
        # Try to get the packet command name from the data
        try:
            command_name = pc.PacketCommand.Name(data[4])
        except ValueError:
            # Log a warning if the command name is not found
            logger.warning(f"Received unsupported packet command: {data[4]}")
            return

        # Log the packet command name and the data
        logger.debug(f"Processing {command_name} packet: {data}")

    # Handle different packet commands
    def process_packet(self, data: bytes):
        # Try to get the packet command name from the data
        try:
            command_name = pc.PacketCommand.Name(data[4])
        except ValueError:
            # Log a warning if the command name is not found
            logger.warning(f"Received unsupported packet command: {data[4]}")
            return

        # Log the packet command name and the data
        logger.debug(f"Processing {command_name} packet: {data}")

        # Handle different packet commands
        match command_name:
            case "C2S_ALIVE_REQ":
                # Send a response for the C2S_ALIVE_REQ packet
                self.respond(pc.SS2C_ALIVE_RES().SerializeToString())
            case "C2S_ACCOUNT_LOGIN_REQ":
                # Process login and store the result in a variable
                login_result = login.process_login(self, data)
                # Log the result
                print("Login result:", login_result)
                # Pass the result to the respond function
                self.respond(login_result)
            case _:
                # Log an error if there is no handler for the received packet
                logger.error(f"Received {command_name} {data} packet but no handler yet")

    def respond(self, data):
        """
        Wrapper that adds the packet header onto the serialized data blob
        and sends the response to the client.
        """
        # Combine the packet header with the serialized data
        response_data = self.packet_header + data
        # Log the response data being sent
        logger.debug(f"Sending response: {response_data}")
        # Send the response data to the client
        self.transport.write(response_data)