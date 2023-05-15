from dndserver.protos.Defines import Define_Common


class State:
    def __init__(self) -> None:
        self.is_ready = False
        self.location = Define_Common.MetaLocation.PLAY
