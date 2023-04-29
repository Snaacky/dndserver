import asyncio
import os

from loguru import logger
from twisted.internet import reactor

from dndserver.config import config
from dndserver.protocol import GameFactory


async def main():
    """Entrypoint where the server first initializes"""
    # Stop the server from executing if the database is missing.
    if not os.path.isfile("dndserver.db"):
        logger.error("dndserver.db doesn't exist, did you run alembic upgrade head?")
        raise SystemExit

    # Sets up the factory for the game server traffic.
    tcpFactory = GameFactory()
    reactor.listenTCP(config.server.port, tcpFactory)

    # Start running the TCP server.
    logger.info(f"Running game server on tcp://{config.server.host}:{config.server.port}")
    reactor.run()


if __name__ == "__main__":
    asyncio.run(main())
