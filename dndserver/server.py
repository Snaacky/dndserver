import asyncio

from loguru import logger
from twisted.internet import reactor

from dndserver import database
from dndserver.config import config
from dndserver.game import GameFactory


async def main():
    """Entrypoint where the server first initializes"""
    # Initializes the database for the first time if it hasn't been already
    database.setup()

    # Sets up the factory for the game server traffic
    tcpFactory = GameFactory()
    reactor.listenTCP(config.server.port, tcpFactory)
    logger.info(f"Running game server on tcp://{config.server.host}:{config.server.port}")
    reactor.run()


if __name__ == "__main__":
    asyncio.run(main())
