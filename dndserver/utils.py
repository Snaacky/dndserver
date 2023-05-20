from typing import Optional, Tuple
import struct
from twisted.internet.interfaces import ITransport

from dndserver.objects.user import User
from dndserver.persistent import sessions
from dndserver.protos import PacketCommand as pc


def make_header(msg: bytes) -> bytes:
    """Create a D&D packet header."""
    # header: <packet length: short> 00 00 <packet id: short> 00 00
    packet_type = type(msg).__name__.replace("SS2C", "S2C").replace("SC2S", "C2S")
    return struct.pack("<HxxHxx", len(msg.SerializeToString()) + 8, pc.PacketCommand.Value(packet_type))


def get_user(
    username: str = None, nickname: str = None, account_id: int = None
) -> Tuple[Optional[ITransport], Optional[User]]:
    """Return a user object based on the account username, character nickname or account ID provided."""
    if not any([username, nickname, account_id]):
        raise Exception("Did not pass username, nickname, or account_id, need at least one")

    for transport, session in sessions.items():
        if (
            username
            and session.account
            and session.account.username == username
            or nickname
            and session.character
            and session.character.nickname == nickname
            or account_id
            and session.account
            and session.account.id == account_id
        ):
            return transport, session

    return None, None


def get_party(
    username: str = None, nickname: str = None, account_id: int = None
) -> Tuple[Optional[ITransport], Optional[User]]:
    """Return a party object based on the account username, character nickname or account ID provided."""
    if not username and not nickname and not account_id:
        raise Exception("Did not pass username, nickname, or account_id, need at least one")

    for _, session in sessions.items():
        if (
            username
            and session.account
            and session.account.username == username
            or nickname
            and session.character
            and session.character.nickname == nickname
            or account_id
            and session.account
            and session.account.id == account_id
        ):
            return session.party

    return None
