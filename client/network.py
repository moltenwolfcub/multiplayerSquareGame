import queue
import socket
from typing import TYPE_CHECKING, Optional

from client.bullet import ClientBullet
from client.pages import page_ids
from client.player import ClientPlayer
from common import packet_ids
from common.c2s_packets import C2SHandshake
from common.packet_base import Packet
from common.packet_header import PacketHeader
from common.s2c_packets import S2CBullets, S2CDisconnectPlayer, S2CHandshake, S2CPlayers, S2CSendID

if TYPE_CHECKING:
    from client.game import Game

class Network:
    def __init__(self, game: 'Game', port: int) -> None:
        self.game = game

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverAddr: str = "127.0.0.1"
        self.port: int = port

        self.recieved_packets: queue.Queue[bytes] = queue.Queue()
        self.quit: bool = False

    def connect(self) -> bool:
        self.conn.connect((self.serverAddr, self.port))
        recieved = self.recv()

        if recieved is None:
            print("No handshake sent from server")
            return False
        
        elif self.handle_packet(recieved) is not None:
            print("Handshake failed (incorrect data recieved) when connecting to server")
            # probably should send back a failure packet but cba rn
            return False

        self.send(C2SHandshake())
        # print("Successfully established connection to server")
        return True
    
    def send(self, packet: Packet) -> None:
        # print(packet.encode())
        PacketHeader.send_packet(self.conn, packet)

    def recv(self) -> Optional[bytes]:
        header = self.conn.recv(PacketHeader.HEADER_SIZE)
        if not header:
            return None

        packet_size = PacketHeader.get_packet_size(header)

        raw_packet = self.conn.recv(packet_size)
        if not raw_packet:
            return None
        
        return raw_packet

    def read_loop(self) -> None:
        while not self.quit:
            try:
                raw_packet = self.recv()

                if raw_packet is None:
                    if not self.quit:
                        print("Disconnected")
                        self.close_connection()
                    break

                self.recieved_packets.put(raw_packet)

            except OSError as e:
                if e.errno == 9:
                    if not self.quit:
                        print("Disconnected")
                        self.close_connection()
                    break
                else:
                    raise e

            except Exception as e:
                print("Network Error: ", e)
                if not self.quit:
                    self.close_connection()
                break

    def packet_loop(self) -> None:
        while not self.quit:
            raw_packet = self.recieved_packets.get()
            self.handle_packet(raw_packet)
            self.recieved_packets.task_done()

    def close_connection(self, needs_closing: bool = True) -> None:
        if self.quit == True:
            return

        self.quit = True

        if needs_closing:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

    def handle_packet(self, raw_packet: bytes) -> Optional[Exception]:
        packet_type = Packet.decode_id(raw_packet)

        
        if packet_type == packet_ids.S2C_HANDSHAKE:
            handshake_packet: S2CHandshake = S2CHandshake.decode_data(raw_packet)

            if not handshake_packet.isCorrect():
                print("Error during handshake")
                return ConnectionError()
            
        elif packet_type == packet_ids.S2C_HANDSHAKE_FAIL:
            print("Server error during handshake. Aborting")
            self.close_connection()
        
        elif packet_type == packet_ids.S2C_PLAYERS:
            players_packet: S2CPlayers = S2CPlayers.decode_data(raw_packet)
            
            client_players: list[ClientPlayer] = []

            for common_player in players_packet.players:
                client_players.append(ClientPlayer.from_common(common_player))
            
            self.game.players = client_players
        
        elif packet_type == packet_ids.S2C_BULLETS:
            bullets_packet: S2CBullets = S2CBullets.decode_data(raw_packet)
            
            client_bullets: list[ClientBullet] = []

            for common_bullet in bullets_packet.bullets:
                client_bullets.append(ClientBullet.from_common(common_bullet))
            
            self.game.bullets = client_bullets
        
        elif packet_type == packet_ids.S2C_SEND_ID:
            id_packet: S2CSendID = S2CSendID.decode_data(raw_packet)

            self.game.this_player_id =  id_packet.player_id
        
        elif packet_type == packet_ids.S2C_PLAYER_DISCONNECT:
            player_disconnect_packet: S2CDisconnectPlayer = S2CDisconnectPlayer.decode_data(raw_packet)

            if player_disconnect_packet.reason == S2CDisconnectPlayer.KICKED:
                print("Kicked by server")

            elif player_disconnect_packet.reason == S2CDisconnectPlayer.SERVER_CLOSED:
                print("Server closed")
            
            elif player_disconnect_packet.reason == S2CDisconnectPlayer.KILLED:
                print("You Died")

            else:
                print(f"Unknown disconnect reason: {player_disconnect_packet.reason}")
            
            self.game.update_server_on_exit = False
            self.game.page_changer(page_ids.PAGE_MENU)

        else:
            print(f"Unknown packet (ID: {packet_type})")
            return ConnectionError()
