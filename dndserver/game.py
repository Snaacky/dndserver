from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver.handlers import login
from dndserver.handlers import character
from dndserver.protos import _PacketCommand_pb2 as pc


class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()


class GameProtocol(Protocol):
    def connectionMade(self):
        logger.debug("Connection made")

    def dataReceived(self, data: bytes):
        logger.debug(f"Received {pc.PacketCommand.Name(data[4])}")
        match pc.PacketCommand.Name(data[4]):
            # TODO: Surely there's a cleaner way that we can do this?
            # TODO: Can we access these enums directly? 'EnumTypeWrapper' object is not callable
            case "C2S_ALIVE_REQ":
                self.send(pc.SS2C_ALIVE_RES().SerializeToString())
            case "C2S_ACCOUNT_LOGIN_REQ":
                res = login.process_login(self, data)
                self.send(self.make_header(res, "S2C_ACCOUNT_LOGIN_RES") + res)
            case "C2S_ACCOUNT_CHARACTER_LIST_REQ":
                res = character.list_characters(self, data)
                self.send(self.make_header(res, "S2C_ACCOUNT_CHARACTER_LIST_RES") + res)
            # case "C2S_ACCOUNT_CHARACTER_CREATE_REQ":
            #    self.send(self.make_header(data) + character.create_character(self, data))
            case _:
                logger.error(f"Received {pc.PacketCommand.Name(data[4])} {data} packet but no handler yet")

    def send(self, data: bytes):
        self.transport.write(data)

    def send_many(self, packets: list):
        for packet in packets:
            self.transport.write(packet)

    def make_header(self, res: bytes, packet_type: str):
        # header: <packet length> 00 00 <packet type> 00 00
        if not res:
            raise Exception("Didn't pass data when creating header")
        packet_type = pc.PacketCommand.Value(packet_type).to_bytes(2, "little")
        packet_length = (len(res) + 8).to_bytes(2, "little")
        logger.debug(packet_length + b"\x00\x00" + packet_type + b"\x00\x00")
        return packet_length + b"\x00\x00" + packet_type + b"\x00\x00"
