import asyncio
import os
import signal
from loguru import logger
from twisted.internet import reactor
import threading


from dndserver.config import config
from dndserver.protocol import GameFactory
from dndserver.console import console


async def main() -> None:
    """Entrypoint where the server first initializes"""
    signal.signal(signal.SIGINT, signal.default_int_handler)
    # Stop the server from executing if the database is missing.
    if not os.path.isfile("dndserver.db"):
        logger.error("dndserver.db doesn't exist, did you run alembic upgrade head?")
        raise SystemExit

    # Sets up the factory for the game server traffic.
    tcpFactory = GameFactory()
    reactor.listenTCP(config.server.port, tcpFactory)

    # Start the console function in a separate thread
    console_thread = threading.Thread(target=console)
    console_thread.start()

    # Start running the TCP server.
    logger.info(f"Running game server on tcp://{config.server.host}:{config.server.port}")
    reactor.run()


if __name__ == "__main__":
    asyncio.run(main())
