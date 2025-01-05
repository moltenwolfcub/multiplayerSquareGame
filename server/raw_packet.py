from server.connection import Connection


class RawPacket:
    def __init__(self, data: bytes, sender: Connection) -> None:
        self.data: bytes = data
        self.sender: Connection = sender
