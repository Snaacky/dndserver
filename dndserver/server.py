import asyncio

from loguru import logger
from twisted.internet import reactor

from dndserver.database import engine
from dndserver.models import base
from dndserver.config import config
from dndserver.protocol import GameFactory


async def main():
    """Entrypoint where the server first initializes"""
    # Creates any missing SQLite tables.
    base.metadata.create_all(engine)

    # Sets up the factory for the game server traffic.
    tcpFactory = GameFactory()
    reactor.listenTCP(config.server.port, tcpFactory)

    # Start running the TCP server.
    logger.info(f"Running game server on tcp://{config.server.host}:{config.server.port}")
    reactor.run()


if __name__ == "__main__":
    asyncio.run(main())
