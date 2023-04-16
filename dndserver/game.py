from binascii import hexlify

from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver.protos import Account_pb2 as account
from dndserver.protos import IronMace_pb2 as ironmace


class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()


class GameProtocol(Protocol):
    def connectionMade(self):
        logger.debug("Connection made")

    def dataReceived(self, data):
        logger.debug(f"Received data: {data}")
        match data:
            #  Received data: b'`\x00\x00\x00\x0b\x00\x02\x00\n\x03asd\x12\x03asd*@4b1bb056f09550f46a4d20314b5858af53bd6c08576f46b6cce68e82cbcef0c0B\n0.5.0.1159'
            case b"\x08\x00\x00\x00\x01\x00\x03\x00":
                self.transport.write(b"\x08\x00\x00\x00\x02\x00\x00\x00")
            case b"\x08\x00\x00\x00\x01\x00\x04\x00":
                self.transport.write(b"\x1e\x00\x00\x00\x0c\x00\x00\x00\x08\x01\x12\x08\x0a\x06\x31\x35\x35\x37\x36\x38\x32\x06\x31\x35\x35\x37\x36\x38\x38\x04")
            case _:
                login = account.SC2S_ACCOUNT_LOGIN_REQ()
                login.ParseFromString(data)
                print(login)
