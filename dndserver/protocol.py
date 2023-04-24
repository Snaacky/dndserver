import struct

from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver.handlers import character, friends, lobby, login, trade, menu, merchant
from dndserver.protos import PacketCommand as pc
from dndserver.sessions import sessions


class GameFactory(Factory):
    def buildProtocol(self, addr) -> Protocol:
        return GameProtocol()


class GameProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()

    def connectionMade(self) -> None:
        """Event for when a client connects to the server."""
        logger.debug(f"Received connection from: {self.transport.client[0]}:{self.transport.client[1]}")
        sessions[self.transport] = {"user": None}

    def connectionLost(self, reason):
        """Event for when a client disconnects from the server."""
        logger.debug(f"Lost connection to: {self.transport.client[0]}:{self.transport.client[1]}")
        del sessions[self.transport]

    def dataReceived(self, data: bytes) -> None:
        """Main loop for receiving request packets and sending response packets."""
        # process all the data
        while len(data):
            # TODO: Implement support for segemented packets based on the incoming data's length.
            length, _id = struct.unpack("<hxxhxx", data[:8])

            # create a message with the correct length
            msg = data[8:length]

            handlers = {
                pc.C2S_ALIVE_REQ: self.heartbeat,
                pc.C2S_ACCOUNT_LOGIN_REQ: login.process_login,
                pc.C2S_ACCOUNT_CHARACTER_CREATE_REQ: character.create_character,
                pc.C2S_ACCOUNT_CHARACTER_DELETE_REQ: character.delete_character,
                pc.C2S_ACCOUNT_CHARACTER_LIST_REQ: character.list_characters,
                pc.C2S_CHARACTER_SELECT_ENTER_REQ: lobby.enter_character_select,
                pc.C2S_CUSTOMIZE_CHARACTER_INFO_REQ: character.character_info,
                pc.C2S_LOBBY_ENTER_REQ: lobby.enter_lobby,
                pc.C2S_FRIEND_LIST_ALL_REQ: friends.list_friends,
                pc.C2S_FRIEND_FIND_REQ: friends.find_user,
                pc.C2S_PARTY_INVITE_REQ: friends.party_invite,
                pc.C2S_META_LOCATION_REQ: menu.process_location,
                pc.C2S_MERCHANT_LIST_REQ: merchant.get_merchant_list,
                pc.C2S_TRADE_MEMBERSHIP_REQUIREMENT_REQ: trade.get_trade_reqs,
                pc.C2S_TRADE_MEMBERSHIP_REQ: trade.process_membership
            }
            handler = [k for k in handlers.keys() if k == _id]
            if not handler:
                return logger.warning(f"Received {pc.PacketCommand.Name(_id)} {data} packet but no handler yet")

            # Heartbeat is handled separately because it doesn't use a header.
            if handler[0] == pc.C2S_ALIVE_REQ:
                return self.heartbeat()

            res = handlers[handler[0]](self, msg)
            self.send(res)

            # remove the data we have processed
            data = data[length:]

    def heartbeat(self):
        """Send a D&D keepalive packet."""
        self.transport.write(pc.SS2C_ALIVE_RES().SerializeToString())

    def make_header(self, msg: bytes):
        """Create a D&D packet header."""
        # header: <packet length: short> 00 00 <packet id: short> 00 00
        packet_type = type(msg).__name__.replace("SS2C", "S2C").replace("SC2S", "C2S")
        return struct.pack("<hxxhxx", len(msg.SerializeToString()) + 8, pc.PacketCommand.Value(packet_type))

    def send(self, msg: bytes):
        """Send a D&D packet to the client."""
        header = self.make_header(msg)
        self.transport.write(header + msg.SerializeToString())
