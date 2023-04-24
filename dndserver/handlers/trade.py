from dndserver.protos import PacketCommand as pc
from dndserver.protos.Trade import (SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES, STRADE_MEMBERSHIP_REQUIREMENT,
                                    SS2C_TRADE_MEMBERSHIP_RES)


def get_trade_reqs(ctx):
    return SS2C_TRADE_MEMBERSHIP_REQUIREMENT_RES(
        # TODO: Unsure what these values are actually supposed to look like.
        requirements=[STRADE_MEMBERSHIP_REQUIREMENT(memberShipType=1, memberShipValue=1)]
    )


def process_membership(ctx, req):
    return SS2C_TRADE_MEMBERSHIP_RES(result=pc.SUCCESS)
