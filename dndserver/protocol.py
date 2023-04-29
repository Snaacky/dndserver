import struct

from loguru import logger
from twisted.internet.protocol import Factory, Protocol

from dndserver.handlers import character, friends, lobby, login, trade, menu, merchant, party, ranking, inventory
from dndserver.objects.user import User
from dndserver.protos import PacketCommand as pc
from dndserver.sessions import sessions
from dndserver.utils import make_header


class GameFactory(Factory):
    def buildProtocol(self, addr) -> Protocol:
        return GameProtocol()


class GameProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()

    def connectionMade(self) -> None:
        """Event for when a client connects to the server."""
        logger.debug(f"Received connection from: {self.transport.client[0]}:{self.transport.client[1]}")
        user = User()
        sessions[self.transport] = user

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
                pc.C2S_CUSTOMIZE_CHARACTER_INFO_REQ: character.character_info,
                pc.C2S_CLASS_PERK_LIST_REQ: character.list_perks,
                pc.C2S_CLASS_SKILL_LIST_REQ: character.list_skills,
                pc.C2S_CLASS_EQUIP_INFO_REQ: character.get_perks_and_skills,
                pc.C2S_CLASS_ITEM_MOVE_REQ: character.move_perks_and_skills,
                pc.C2S_CLASS_LEVEL_INFO_REQ: character.get_experience,
                pc.C2S_INVENTORY_SINGLE_UPDATE_REQ: inventory.move_single_item,
                pc.C2S_INVENTORY_MOVE_REQ: inventory.move_item,
                pc.C2S_LOBBY_ENTER_REQ: lobby.enter_lobby,
                pc.C2S_CHARACTER_SELECT_ENTER_REQ: lobby.enter_character_select,
                pc.C2S_FRIEND_LIST_ALL_REQ: friends.list_friends,
                pc.C2S_FRIEND_FIND_REQ: friends.find_user,
                pc.C2S_META_LOCATION_REQ: menu.process_location,
                pc.C2S_MERCHANT_LIST_REQ: merchant.get_merchant_list,
                pc.C2S_MERCHANT_STOCK_BUY_ITEM_LIST_REQ: merchant.get_buy_list,
                pc.C2S_MERCHANT_STOCK_SELL_BACK_ITEM_LIST_REQ: merchant.get_sellback_list,
                pc.C2S_PARTY_INVITE_REQ: party.party_invite,
                pc.C2S_PARTY_INVITE_ANSWER_REQ: party.accept_invite,
                pc.C2S_TRADE_MEMBERSHIP_REQUIREMENT_REQ: trade.get_trade_reqs,
                pc.C2S_TRADE_MEMBERSHIP_REQ: trade.process_membership,
                pc.C2S_RANKING_RANGE_REQ: ranking.get_ranking,
                pc.C2S_RANKING_CHARACTER_REQ: ranking.get_character_ranking,
            }
            handler = [k for k in handlers.keys() if k == _id]
            if not handler:
                return logger.warning(f"Received {pc.PacketCommand.Name(_id)} {data} packet but no handler yet")

            # Heartbeat is handled separately because it doesn't use a header.
            if handler[0] == pc.C2S_ALIVE_REQ:
                return self.heartbeat()

            res = handlers[handler[0]](self, msg)
            self.reply(msg=res)

            # remove the data we have processed
            data = data[length:]

    def heartbeat(self):
        """Send a D&D keepalive packet."""
        self.transport.write(pc.SS2C_ALIVE_RES().SerializeToString())

    def reply(self, msg: bytes):
        """Send a D&D packet to the current context transport."""
        header = make_header(msg)
        self.transport.write(header + msg.SerializeToString())

    def send(self, transport, msg: bytes):
        """Send a D&D packet to a specific transport."""
        header = make_header(msg)
        sessions[transport].write(header + msg.SerializeToString())
