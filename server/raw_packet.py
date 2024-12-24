import socket

class RawPacket:
    def __init__(self, data: bytes, sender: socket.socket) -> None:
        self.data: bytes = data
        self.sender: socket.socket = sender
