import _thread
import queue
import socket
import sys
import time
from typing import Optional

from common import packet_ids
from common.c2s_packets import C2SHandshake, C2SMovementUpdate
from common.packet_base import Packet
from common.packet_header import PacketHeader
from common.s2c_packets import S2CFailedHandshake, S2CHandshake, S2CPlayers
from server.game_data import GameData
from server.raw_packet import RawPacket


class Server:

    def __init__(self, port: int = 0) -> None:
        self.server: str = "127.0.0.1"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.port: int = port

        self.recieved_packets: queue.Queue[RawPacket] = queue.Queue()
        self.quit: bool = False

        self.open_connections: dict[socket.socket, int] = {}

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
            conn, addr = self.socket.accept()

            print(f"Connecting to: {addr}")

            _thread.start_new_thread(self.read_loop, (conn,))
    
    def read_loop(self, conn: socket.socket) -> None:
        '''One per client to store received packets for later processing'''
        if self.initial_handshake(conn) is not None:
            return
        
        self.on_client_join(conn)

        while not self.quit:
            try:
                raw_packet = self.recv(conn)
                if raw_packet is None:
                    self.close_connection(conn)
                    break

                self.recieved_packets.put(RawPacket(raw_packet, conn))

            except ConnectionResetError:
                self.close_connection(conn)
                break

            except Exception as e:
                self.close_connection(conn)
                print("Network Error: ", e)
                break
        
        # once players are properly linked to clients change to a client disconnect message
        print(f"Lost connection to peer")
        self.on_client_disconnect(conn)
    
    def packet_loop(self) -> None:
        '''Processes all recieved packets'''
        while not self.quit:
            raw_packet = self.recieved_packets.get()
            self.handle_packet(raw_packet)
            self.recieved_packets.task_done()

    def initial_handshake(self, conn: socket.socket) -> Optional[Exception]:
        PacketHeader.send_packet(conn, S2CHandshake())
        try:
            check_packet = self.recv(conn)
        except ConnectionResetError:
            print(f"Error during response from closed peer.")
            self.close_connection(conn)
            return ConnectionError()

        if check_packet is None:
            print(f"No response to handshake from peer: {conn.getpeername()}")
            PacketHeader.send_packet(conn, S2CFailedHandshake())
            time.sleep(0.1) # time for client to close on their end
            self.close_connection(conn)
            return ConnectionError()
        
        if self.handle_packet(RawPacket(check_packet, conn)) is not None:
            print(f"Handshake failed (incorrect data recieved) when connecting to peer: {conn.getpeername()}")
            PacketHeader.send_packet(conn, S2CFailedHandshake())
            time.sleep(0.1) # time for client to close on their end
            self.close_connection(conn)
            return ConnectionError()
        
        print(f"Connection established to peer: {conn.getpeername()}")

    def close_server(self) -> None:
        self.quit = True

    def close_connection(self, conn: socket.socket) -> None:
        try:
            conn.close()
        except:
            print("Error while closing connection")
        
    def get_free_id(self) -> int:
        id = 0
        while True:
            if list(self.open_connections.values()).count(id) == 0:
                return id
            id += 1

    def broadcast(self, packet: Packet) -> None:
        for c in self.open_connections:
            try:
                PacketHeader.send_packet(c, packet)
            except BrokenPipeError:
                pass
            except OSError as e:
                if e.errno == 9:
                    pass # client has disconnected but server hasn't caught up yet
                else:
                    raise e
    
    def recv(self, conn: socket.socket) -> Optional[bytes]:
        header = conn.recv(PacketHeader.HEADER_SIZE)
        if not header:
            return None

        packet_size = PacketHeader.get_packet_size(header)

        raw_packet = conn.recv(packet_size)
        if not raw_packet:
            return None
        
        # printBytes(rawPacket)
        return raw_packet

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

    def on_client_join(self, conn: socket.socket) -> None:
        id = self.get_free_id()
        self.open_connections[conn] = id

        self.game.add_random_player(id)

        self.broadcast(S2CPlayers(self.game.players))
    
    def on_client_disconnect(self, conn: socket.socket) -> None:
        id = self.open_connections.pop(conn, None)

        if id is None:
            return # connection was never in list

        self.game.remove_player(id)

        self.broadcast(S2CPlayers(self.game.players))

    def main_loop(self) -> None:
        '''Handles main game logic separate from network events'''
        while not self.quit:
            tick_start = time.perf_counter_ns()

            self.game.update()

            tick_stop = time.perf_counter_ns()
            time_remaining_ns = self.game.settings.tick_time_ns - (tick_stop-tick_start)

            if time_remaining_ns > 0:
                time.sleep(time_remaining_ns//1_000_000_000)

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

                case "c" | "connections":
                    print("CONNECTIONS:")
                    for c, id in self.open_connections.items():
                        print(f"- {id}: {c}") 

                    if len(self.game.players) == 0:
                        print("empty")

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
                PacketHeader.send_packet(raw_packet.sender, S2CPlayers(self.game.players))
            
            case packet_ids.C2S_MOVEMENT_UPDATE:
                movement_packet: C2SMovementUpdate = C2SMovementUpdate.decode_data(raw_packet.data)

                player = self.game.get_player(self.open_connections[raw_packet.sender])
                if player is None:
                    print(f"Error! No player assosiated with connection: {raw_packet.sender}")
                    return LookupError()
                
                player.mov_dir = movement_packet.mov_dir
            
            case packet_ids.C2S_CREATE_BULLET:
                shooting_player = self.game.get_player(self.open_connections[raw_packet.sender])

                if shooting_player is None:
                    print(f"Error! No player assosiated with connection: {raw_packet.sender}")
                    return LookupError()

                print(f"Pow from {shooting_player.pos}")

            case _:
                print(f"Unknown packet (ID: {packet_type})")
                return ConnectionError()
