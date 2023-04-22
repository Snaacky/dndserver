import asyncio

from loguru import logger
from twisted.internet import reactor

from dndserver import database
from dndserver.config import config
from dndserver.protocol import GameFactory


async def main():
    """Entrypoint where the server first initializes"""
    # Attempts to initialize the database for the first time.
    database.setup()

    # Sets up the factory for the game server traffic.
    tcpFactory = GameFactory()
    reactor.listenTCP(config.server.port, tcpFactory)

    # Start running the TCP server.
    logger.info(f"Running game server on tcp://{config.server.host}:{config.server.port}")
    reactor.run()