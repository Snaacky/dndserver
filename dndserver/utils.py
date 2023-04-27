import struct

from loguru import logger

from dndserver.parties import parties
from dndserver.protos import PacketCommand as pc
from dndserver.sessions import sessions


def make_header(msg: bytes):
    """Create a D&D packet header."""
    # header: <packet length: short> 00 00 <packet id: short> 00 00
    packet_type = type(msg).__name__.replace("SS2C", "S2C").replace("SC2S", "C2S")
    return struct.pack("<HxxHxx", len(msg.SerializeToString()) + 8, pc.PacketCommand.Value(packet_type))


def get_user_by_nickname(nickname: str):
    """Find a user's connection by nickname."""
    for transport, session in sessions.items():
        if session.character and session.character.nickname == nickname:
            return transport, session
    return None, None


def get_user_by_account_id(account_id: int):
    """Find a user's connection by account ID."""
    for transport, session in sessions.items():
        if session.account and session.account.id == account_id:
            return transport, session
    return None, None


def get_party_by_account_id(account_id: int):
    transport, session = get_user_by_account_id(account_id)
    return session.party
