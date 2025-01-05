import socket


class Connection:

    def __init__(self, s: socket.socket) -> None:
        self.socket: socket.socket = s

        self.player_id: int = -1

        self.is_open: bool = False
        
    def __str__(self) -> str:
        return f"Conn[id= {self.player_id}, name= {self.get_peer_name()}, open= {self.is_open}]"

    def open_connection(self, player_id: int) -> None:
        self.player_id = player_id
        self.is_open = True

    def get_peer_name(self) -> str:
        return self.socket.getpeername()

    def close(self) -> None:
        self.socket.close()
        
