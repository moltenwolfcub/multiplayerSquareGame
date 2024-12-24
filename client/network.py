import queue
import socket
import sys
from typing import TYPE_CHECKING, Optional

from client.player import ClientPlayer
from common import packet_ids
from common.c2s_packets import C2SHandshake, C2SMovementUpdate
from common.data_types import Vec2D
from common.packet_base import Packet
from common.packet_header import PacketHeader
from common.s2c_packets import S2CHandshake, S2CPlayers

if TYPE_CHECKING:
    from client.main import Game

class Network:
    def __init__(self, game: 'Game', port: int) -> None:
        self.game = game

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server: str = "127.0.0.1"
        self.port: int = port

        self.recieved_packets: queue.Queue[bytes] = queue.Queue()
        self.quit: bool = False

    def connect(self) -> None:
        self.client.connect((self.server, self.port))
        recieved = self.recv()

        if recieved is None:
            print("No handshake sent from server")
            self.close_connection()
        
        elif self.handle_packet(recieved) is not None:
            print("Handshake failed (incorrect data recieved) when connecting to server")
            # probably should send back a failure packet but cba rn
            self.close_connection()
        
        if self.quit:
            sys.exit()

        self.send(C2SHandshake())
        print("Successfully established connection to server")
    
    def send(self, packet: Packet) -> None:
        # print(packet.encode())
        PacketHeader.send_packet(self.client, packet)

    def recv(self) -> Optional[bytes]:
        header = self.client.recv(PacketHeader.HEADER_SIZE)
        if not header:
            return None

        packet_size = PacketHeader.get_packet_size(header)

        raw_packet = self.client.recv(packet_size)
        if not raw_packet:
            return None
        
        return raw_packet

    def read_loop(self) -> None:
        while not self.quit:
            try:
                raw_packet = self.recv()

                if raw_packet is None:
                    print("Disconnected")
                    self.close_connection()
                    break

                self.recieved_packets.put(raw_packet)

            except OSError as e:
                if e.errno == 9:
                    print("Disconnected")
                    self.close_connection()
                    break
                else:
                    raise e

            except Exception as e:
                print("Network Error: ", e)
                self.close_connection()
                break

    def packet_loop(self) -> None:
        while not self.quit:
            raw_packet = self.recieved_packets.get()
            self.handle_packet(raw_packet)
            self.recieved_packets.task_done()

    def close_connection(self) -> None:
        try:
            self.client.close()
        except:
            pass

        self.quit = True

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

    def handle_packet(self, raw_packet: bytes) -> Optional[Exception]:
        packet_type = Packet.decode_id(raw_packet)

        match packet_type:
            case packet_ids.S2C_HANDSHAKE:
                handshake_packet: S2CHandshake = S2CHandshake.decode_data(raw_packet)

                if not handshake_packet.isCorrect():
                    print("Error during handshake")
                    return ConnectionError()
                
            case packet_ids.S2C_HANDSHAKE_FAIL:
                print("Server error during handshake. Aborting")
                self.close_connection()
            
            case packet_ids.S2C_PLAYERS:
                players_packet: S2CPlayers = S2CPlayers.decode_data(raw_packet)
                
                client_players: list[ClientPlayer] = []

                for common_player in players_packet.players:
                    client_players.append(ClientPlayer.from_common(common_player, self.game))
                
                self.game.players = client_players

            case _:
                print(f"Unknown packet (ID: {packet_type})")
                return ConnectionError()
    
    def send_updates(self) -> None:
        if self.game.movement_codes_dirty:
            dx = self.game.movement_codes[3] - self.game.movement_codes[2]
            dy = self.game.movement_codes[1] - self.game.movement_codes[0]
            self.send(C2SMovementUpdate(Vec2D(dx,dy)))

            self.game.movement_codes_dirty = False
