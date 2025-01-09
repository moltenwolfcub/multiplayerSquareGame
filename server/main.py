import _thread
import queue
import socket
import sys
import time
from typing import Optional

from common import packet_ids
from common.bullet import CommonBullet
from common.c2s_packets import C2SCreateBullet, C2SHandshake, C2SMovementUpdate
from common.packet_base import Packet
from common.packet_header import PacketHeader
from common.s2c_packets import S2CBullets, S2CFailedHandshake, S2CHandshake, S2CPlayers, S2CSendID
from server.connection import Connection
from server.game_data import GameData
from server.raw_packet import RawPacket
from server.settings import Settings


class Server:

    def __init__(self, port: int = 0) -> None:
        self.server: str = "127.0.0.1"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.port: int = port

        self.recieved_packets: queue.Queue[RawPacket] = queue.Queue()
        self.quit: bool = False

        self.open_connections: list[Connection] = []

        self.game: GameData = GameData(self)

    def start(self) -> None:
        try:
            self.socket.bind((self.server, self.port))
        except socket.error as e:
            print(e)
            self.close_server()
            return
        
        self.socket.listen()
        print(f"Server started on port {self.socket.getsockname()[1]}")

        _thread.start_new_thread(self.console_loop, ())
        _thread.start_new_thread(self.main_loop, ())
        _thread.start_new_thread(self.packet_loop, ())
        _thread.start_new_thread(self.accept_loop, ())
        
        while not self.quit: pass
        sys.exit()


    def accept_loop(self) -> None:
        '''Handles accepting new clients'''
        while not self.quit:
            sock, addr = self.socket.accept()
            conn: Connection = Connection(sock)

            print(f"Connecting to: {addr}")

            _thread.start_new_thread(self.read_loop, (conn,))
    
    def read_loop(self, conn: Connection) -> None:
        '''One per client to store received packets for later processing'''
        if self.initial_handshake(conn) is not None:
            return
        
        self.on_client_join(conn)

        while not self.quit:
            try:
                raw_packet = self.recv(conn)
                if raw_packet is None:
                    print(f"Lost connection to peer")
                    self.close_connection(conn)
                    break

                self.recieved_packets.put(RawPacket(raw_packet, conn))

            except ConnectionResetError:
                print(f"Lost connection to peer")
                self.close_connection(conn)
                break

            except Exception as e:
                self.close_connection(conn)
                print("Network Error: ", e)
                break
    
    def packet_loop(self) -> None:
        '''Processes all recieved packets'''
        while not self.quit:
            raw_packet = self.recieved_packets.get()
            self.handle_packet(raw_packet)
            self.recieved_packets.task_done()

    def initial_handshake(self, conn: Connection) -> Optional[Exception]:
        self.send(conn, S2CHandshake())
        try:
            check_packet = self.recv(conn)
        except ConnectionResetError:
            print(f"Error during response from closed peer.")
            self.close_connection(conn, was_open=False)
            return ConnectionError()

        if check_packet is None:
            print(f"No response to handshake from peer: {conn.get_peer_name()}")
            self.send(conn, S2CFailedHandshake())
            time.sleep(0.1) # time for client to close on their end
            self.close_connection(conn, was_open=False)
            return ConnectionError()
        
        if self.handle_packet(RawPacket(check_packet, conn)) is not None:
            print(f"Handshake failed (incorrect data recieved) when connecting to peer: {conn.get_peer_name()}")
            self.send(conn, S2CFailedHandshake())
            time.sleep(0.1) # time for client to close on their end
            self.close_connection(conn, was_open=False)
            return ConnectionError()
        
        print(f"Connection established to peer: {conn.get_peer_name()}")

    def close_server(self) -> None:
        self.quit = True

    def close_connection(self, conn: Connection, was_open: bool = True, shutdown: bool = True) -> None:
        conn.close(shutdown)
        if was_open:
            self.on_client_disconnect(conn)
        
    def get_free_id(self) -> int:
        id = 0
        while True:
            if len([c for c in self.open_connections if c.player_id == id]) == 0:
                return id
            id += 1

    def broadcast(self, packet: Packet) -> None:
        for c in self.open_connections:
            try:
                self.send(c, packet)
            except BrokenPipeError:
                pass
            except OSError as e:
                if e.errno == 9:
                    pass # client has disconnected but server hasn't caught up yet
                else:
                    raise e
    
    def recv(self, conn: Connection) -> Optional[bytes]:
        header = conn.socket.recv(PacketHeader.HEADER_SIZE)
        if not header:
            return None

        packet_size = PacketHeader.get_packet_size(header)

        raw_packet = conn.socket.recv(packet_size)
        if not raw_packet:
            return None
        
        # printBytes(rawPacket)
        return raw_packet
    
    def send(self, conn: Connection, packet: Packet) -> None:
        PacketHeader.send_packet(conn.socket, packet)

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

    def on_client_join(self, conn: Connection) -> None:
        id = self.get_free_id()
        conn.open_connection(id)
        self.open_connections.append(conn)
        self.send(conn, S2CSendID(id))

        self.game.add_random_player(id)

        self.broadcast(S2CPlayers(self.game.players))
    
    def on_client_disconnect(self, conn: Connection) -> None:
        id = conn.player_id
        try:
            self.open_connections.remove(conn)
        except:
            return # connection was never in list

        if id == -1:
            print("Error removing client. connection was opened but ID wasn't set")

        self.game.remove_player(id)

        self.broadcast(S2CPlayers(self.game.players))

    def main_loop(self) -> None:
        '''Handles main game logic separate from network events'''
        while not self.quit:
            tick_start = time.perf_counter_ns()

            self.game.update()

            tick_stop = time.perf_counter_ns()
            time_remaining_ns = Settings.tick_time_ns - (tick_stop-tick_start)

            if time_remaining_ns > 0:
                time.sleep(time_remaining_ns/1_000_000_000)

    def console_loop(self) -> None:
        '''Handles server console commands'''
        while not self.quit:
            console_input: str = input().lower().strip()

            match console_input:
                case "q" | "quit":
                    self.close_server()

                case "p" | "players":
                    print("PLAYERS:")
                    for p in self.game.players:
                        print(f"- {p}")

                    if len(self.game.players) == 0:
                        print("empty")

                case "b" | "bullets":
                    print("BULLETS:")
                    for b in self.game.bullets:
                        print(f"- {b}")

                    if len(self.game.bullets) == 0:
                        print("empty")

                case "c" | "connections":
                    print("CONNECTIONS:")
                    for c in self.open_connections:
                        print(f"- {c}") 

                    if len(self.open_connections) == 0:
                        print("empty")

                case "k" | "kick":
                    print("CLEARING")
                    for c in self.open_connections:
                        self.close_connection(c)

                case _:
                    pass

    def handle_packet(self, raw_packet: RawPacket) -> Optional[Exception]:
        packet_type: int = Packet.decode_id(raw_packet.data)

        match packet_type:
            case packet_ids.C2S_HANDSHAKE:
                handshake_packet: C2SHandshake = C2SHandshake.decode_data(raw_packet.data)

                if not handshake_packet.isCorrect():
                    print("Error during handshake")
                    return ConnectionError()
            
            case packet_ids.C2S_PLAYER_REQUEST:
                self.send(raw_packet.sender, S2CPlayers(self.game.players))
            
            case packet_ids.C2S_MOVEMENT_UPDATE:
                movement_packet: C2SMovementUpdate = C2SMovementUpdate.decode_data(raw_packet.data)

                player = self.game.get_player(raw_packet.sender.player_id)
                if player is None:
                    print(f"Error! No player assosiated with connection: {raw_packet.sender}")
                    return LookupError()
                
                player.mov_dir = movement_packet.mov_dir
            
            case packet_ids.C2S_CREATE_BULLET:
                bullet_packet: C2SCreateBullet = C2SCreateBullet.decode_data(raw_packet.data)

                shooting_player = self.game.get_player(raw_packet.sender.player_id)

                if shooting_player is None:
                    print(f"Error! No player assosiated with connection: {raw_packet.sender}")
                    return LookupError()

                self.game.bullets.append(CommonBullet(shooting_player.pos.clone(), bullet_packet.angle))

                self.broadcast(S2CBullets(self.game.bullets))
            
            case packet_ids.C2S_CLIENT_DISCONNECT:
                self.close_connection(raw_packet.sender, shutdown=False)

            case _:
                print(f"Unknown packet (ID: {packet_type})")
                return ConnectionError()
