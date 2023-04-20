import asyncio

from loguru import logger
from twisted.internet import reactor

from dndserver.config import config
from dndserver.game import GameFactory


async def main():
    tcpFactory = GameFactory()
    reactor.listenTCP(config.server.port, tcpFactory)
    logger.info(f"Running game server on tcp://{config.server.host}:{config.server.port}")
    reactor.run()