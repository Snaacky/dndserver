# starting id for the trading
trade_id = 0


class TradeParty:
    def __init__(self, ctx=None) -> None:
        self.ctx = ctx
        self.is_ready = False
        self.inventory = []


class Trade:
    def __init__(self, user0=TradeParty(), user1=TradeParty()) -> None:
        global trade_id
        trade_id += 1
        self.id = trade_id

        self.user0 = user0
        self.user1 = user1
