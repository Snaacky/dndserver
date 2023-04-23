import struct

from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver.handlers import character, friends, lobby, login
# from dndserver.protos import _Character_pb2 as char
from dndserver.protos import Defines as df
from dndserver.protos import PacketCommand as pc
from dndserver.protos import Account as acc
# from dndserver.protos import Common_pb2 as common
from dndserver.protos import Friend as friend
from dndserver.protos import Party as party
# from dndserver.protos import Ranking_pb2 as rank
from dndserver.protos import Trade as trade


class GameFactory(Factory):
    def buildProtocol(self, addr):
        return GameProtocol()


class GameProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()
        # Where all of the game server related connection session
        # data is stored.
        self.sessions = {}

    def connectionMade(self):
        """Event for when a client connects to the server."""
        logger.debug("Connection made")
        self.sessions[self.transport] = {"accountId": 0}

    def dataReceived(self, data: bytes):
        """Main loop for receiving request packets and sending response packets."""
        # TODO: Surely there's a cleaner way that we can do this?
        # TODO: Can we access these enums directly? 'EnumTypeWrapper' object is not callable
        # TODO: Implement support for segemented packets based on the incoming datas length.
        # We need to parse the header to see the length of the packet and the ID.
        length, _id = struct.unpack("<hxxhxx", data[:8])
        msg = data[8:]

        match pc.PacketCommand.Name(_id):

            # Heartbeat sent between the client and server every second.
            case "C2S_ALIVE_REQ":
                self.transport.write(pc.SS2C_ALIVE_RES().SerializeToString())

            # Login attempt from the client.
            case "C2S_ACCOUNT_LOGIN_REQ":
                req = acc.SC2S_ACCOUNT_LOGIN_REQ()
                req.ParseFromString(msg)
                res = login.process_login(self, req).SerializeToString()
                header = self.make_header(res, "S2C_ACCOUNT_LOGIN_RES")
                self.sessions[self.transport]["state"] = df.Define_Common.CHARACTER_SELECT
                self.send(header, res)

            # Sends character list to the character screen and sends character information
            # when in the lobby/tavern.
            case "C2S_ACCOUNT_CHARACTER_LIST_REQ":
                req = acc.SC2S_ACCOUNT_CHARACTER_LIST_REQ()
                req.ParseFromString(msg)
                res = character.list_characters(self, req).SerializeToString()
                header = self.make_header(res, "S2C_ACCOUNT_CHARACTER_LIST_RES")
                self.send(header, res)

            # Character creation attempt from the client.
            case "C2S_ACCOUNT_CHARACTER_CREATE_REQ":
                req = acc.SC2S_ACCOUNT_CHARACTER_CREATE_REQ()
                req.ParseFromString(msg)
                res = character.create_character(self, req).SerializeToString()
                header = self.make_header(res, "S2C_ACCOUNT_CHARACTER_CREATE_RES")
                self.send(header, res)

            # Character deletion attempt from the client.
            case "C2S_ACCOUNT_CHARACTER_DELETE_REQ":
                req = acc.SC2S_ACCOUNT_CHARACTER_DELETE_REQ()
                req.ParseFromString(msg)
                res = character.delete_character(self, req).SerializeToString()
                header = self.make_header(res, "S2C_ACCOUNT_CHARACTER_DELETE_RES")
                self.send(header, res)

            # Client attempting to load into the lobby.
            case "C2S_LOBBY_ENTER_REQ":
                req = acc.SC2S_LOBBY_ENTER_REQ()
                req.ParseFromString(msg)
                res = lobby.enter_lobby(req).SerializeToString()
                header = self.make_header(res, "S2C_LOBBY_ENTER_RES")
                self.send(header, res)
                self.sessions[self.transport]["state"] = df.Define_Common.PLAY

            case "C2S_CUSTOMIZE_CHARACTER_INFO_REQ":
                res = character.character_info(self).SerializeToString()
                header = self.make_header(res, "S2C_LOBBY_CHARACTER_INFO_RES")
                self.send(header, res)

            # case "C2S_RANKING_RANGE_REQ":
            #     logger.error(req.hex())
            #     req = rank.SC2S_RANKING_RANGE_REQ()
            #     req.ParseFromString(msg)
            #     res = ranking.get_ranking(self, data)

            case "C2S_TRADE_MEMBERSHIP_REQUIREMENT_REQ":
                requirement = trade.STRADE_MEMBERSHIP_REQUIREMENT(
                    memberShipType=1,
                    memberShipValue=1
                )
                res = trade.SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES(
                    requirements=[requirement]
                ).SerializeToString()
                header = self.make_header(res, "S2C_TRADE_MEMBERSHIP_REQUIREMENT_RES")
                self.send(header, res)

            case "C2S_TRADE_MEMBERSHIP_REQ":
                req = trade.SC2S_TRADE_MEMBERSHIP_REQ()
                req.ParseFromString(msg)
                logger.debug(f"Received: {msg} for C2S_TRADE_MEMBERSHIP_REQ")
                res = trade.SS2C_TRADE_MEMBERSHIP_RES(result=1).SerializeToString()
                header = self.make_header(res, "S2C_TRADE_MEMBERSHIP_RES")
                self.send(header, res)

            case "C2S_META_LOCATION_REQ":
                logger.debug(f"Raw hex bytes {msg} for C2S_META_LOCATION_REQ")
                logger.debug(f"Hexlified bytes {msg.hex()} for C2S_META_LOCATION_REQ")

                # For some reason on certain screens like merchant, rankings, etc., the message
                # does not parse against the meta location request protobuf and fails. The
                # failing message seems to contain the location as the second byte in the message
                # as a char. For some reason the message does not parse when the last 4 bytes
                # exist in that message but removing them works.

                # Problematic message example:
                # Raw hex bytes b'\x08\x05\x08\x00\x00\x00G\x055\x00' for C2S_META_LOCATION_REQ
                # Hexlified bytes 08050800000047053500 for C2S_META_LOCATION_REQ

                # Error in protobuf-inspector:
                # Exception: Unknown wire type 7
                # 0000   08 05 08 00 00 00 47 05 35 00       ......G.5.

                # protobuf-inspector output With last 4 bytes removed:
                # root:
                # 1 <varint> = 5
                # 1 <varint> = 0
                # 0 <varint> = 0

                # req = common.SC2S_META_LOCATION_REQ()
                # req.ParseFromString(location)

                # location = int.from_bytes(struct.unpack("<xc", msg[:3])[0], "little")
                # self.sessions[self.transport]["state"] = df.Define_Common.MetaLocation.Name(location)

                # res = common.SS2C_META_LOCATION_RES(location=location).SerializeToString()
                # header = self.make_header(res, "S2C_META_LOCATION_RES")
                # self.send(header, res)

            # Occurs when a user opens the friends list system.
            case "C2S_FRIEND_LIST_ALL_REQ":
                res = friends.list_friends(ctx=self).SerializeToString()
                header = self.make_header(res, "S2C_FRIEND_LIST_ALL_RES")
                self.send(header, res)

            # Occurs when a user searches for another user by name.
            case "C2S_FRIEND_FIND_REQ":
                req = friend.SC2S_FRIEND_FIND_REQ()
                req.ParseFromString(msg)
                res = friends.find_user(ctx=self, req=req).SerializeToString()
                header = self.make_header(res, "S2C_FRIEND_FIND_RES")
                self.send(header, res)

            # Occurs when a user invites another user to their party.
            case "C2S_PARTY_INVITE_REQ":
                req = party.SC2S_PARTY_INVITE_REQ()
                req.ParseFromString(msg)

                res = friends.party_invite(ctx=self, req=req).SerializeToString()
                header = self.make_header(res, "S2C_PARTY_INVITE_RES")
                self.send(header, res)

                res = friends.party_invite_notify(ctx=self, req=req).SerializeToString()
                header = self.make_header(res, "S2C_PARTY_INVITE_NOT")
                self.send(header, res)

            # case "C2S_PARTY_INVITE_ANSWER_REQ":
                
            
            # All other currently unhandled packets.
            case _:
                logger.warning(f"Received {pc.PacketCommand.Name(_id)} {data} packet but no handler yet")

    def send(self, header: bytes, body: bytes):
        """Send a D&D packet to the client."""
        self.transport.write(header + body)

    def connectionLost(self, reason):
        """Event for when a client disconnects from the server."""
        return NotImplementedError

    def make_header(self, res: bytes, packet_id: str):
        """Create a D&D packet header."""
        # header: <packet length: short> 00 00 <packet id: short> 00 00
        if not res:
            raise Exception("Didn't pass data when creating header")
        return struct.pack("<hxxhxx", len(res) + 8, pc.PacketCommand.Value(packet_id))
