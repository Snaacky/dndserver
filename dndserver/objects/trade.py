from dndserver.persistent import trades


class TradeParty:
    def __init__(self, ctx=None) -> None:
        self.ctx = ctx
        self.is_ready = False
        self.inventory = []


class Trade:
    def __init__(self, user0=TradeParty(), user1=TradeParty()) -> None:
        self.id = len(trades) + 1
        self.user0 = user0
        self.user1 = user1
