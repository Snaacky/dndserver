import asyncio
import os
import signal
from loguru import logger
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import threading
import binascii
import struct

from dndserver.config import config
from dndserver.protocol import GameFactory
from dndserver.console import console
from dndserver.matchmaking import matchmaking



async def main():
    """Entrypoint where the server first initializes"""
    signal.signal(signal.SIGINT, signal.default_int_handler)
    # Stop the server from executing if the database is missing.
    if not os.path.isfile("dndserver.db"):
        logger.error("dndserver.db doesn't exist, did you run alembic upgrade head?")
        raise SystemExit

    # Sets up the factory for the game server traffic.
    tcpFactory = GameFactory()
    reactor.listenTCP(config.server.port, tcpFactory)

    # Start the matchmaking function in a separate thread
    # matchmaking_thread = threading.Thread(target=matchmaking)
    # matchmaking_thread.start()

    # Start the console function in a separate thread
    console_thread = threading.Thread(target=console)
    console_thread.start()

    reactor.listenUDP(9999, Echo())
    reactor.run()
    # Start running the TCP server.
    logger.info(f"Running game server on tcp://{config.server.host}:{config.server.port}")
    reactor.run()


class Echo(DatagramProtocol):
    def datagramReceived(self, data, address):
        if len(data) < 24:
            print("Received non-UE5 packet from {}: {}".format(address, data))
            return

        header = struct.unpack_from("<QIIBBBI", data, 0)

        packet_size = header[0]  # Size of the entire packet, including header
        packet_seq = header[1]  # Sequence number of the packet
        packet_ack = header[2]  # Acknowledgement number of the packet
        packet_flags = header[3]  # Packet flags
        packet_channel = header[4]  # Channel index
        packet_chSequence = header[5]  # Channel sequence number
        packet_messageType = header[6]  # Message type

        payload = data[24:]
        print(data)
        print(
            "Received UE5 packet from {}: size={}, seq={}, ack={}, flags={}, channel={}, chSequence={}, messageType={}, payload={}".format(
                address,
                packet_size,
                packet_seq,
                packet_ack,
                packet_flags,
                packet_channel,
                packet_chSequence,
                packet_messageType,
                binascii.hexlify(payload),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
