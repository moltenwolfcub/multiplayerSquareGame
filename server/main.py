import _thread
import queue
import random
import socket
import sys
import time
from typing import Optional

from common import packetIDs
from common.c2sPackets import C2SHandshake
from common.packetBase import Packet
from common.player import CommonPlayer
from common.s2cPackets import S2CFailedHandshake, S2CHandshake, S2CPlayers
from server.gameData import GameData
from server.rawPacket import RawPacket


class Server:

	def __init__(self, port: int = 0) -> None:
		self.server: str = "127.0.0.1"
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.port: int = port

		self.recievedPackets: queue.Queue[RawPacket] = queue.Queue()
		self.quit: bool = False

		self.openConnections: list[socket.socket] = []

		self.game: GameData = GameData()

	def start(self) -> None:
		try:
			self.socket.bind((self.server, self.port))
		except socket.error as e:
			print(e)
			self.closeServer()
		
		self.socket.listen()
		print(f"Server started on port {self.socket.getsockname()[1]}")

		_thread.start_new_thread(self.consoleLoop, ())
		_thread.start_new_thread(self.mainLoop, ())
		_thread.start_new_thread(self.packetLoop, ())
		_thread.start_new_thread(self.acceptLoop, ())
		
		while not self.quit: pass
		sys.exit()


	def acceptLoop(self) -> None:
		'''Handles accepting new clients'''
		while not self.quit:
			conn, addr = self.socket.accept()

			print(f"Connecting to: {addr}")

			_thread.start_new_thread(self.readLoop, (conn,))
	
	def readLoop(self, conn: socket.socket) -> None:
		'''One per client to store received packets for later processing'''
		if self.initialHandshake(conn) is not None:
			return
		
		self.openConnections.append(conn)

		while not self.quit:
			try:
				rawData = conn.recv(2048)

				if not rawData:
					print("Disconnected")
					break

				self.recievedPackets.put(RawPacket(rawData, conn))

			except:
				break
		
		print(f"Lost connection to peer: {conn.getpeername()}")
		self.openConnections.remove(conn)
		conn.close()
	
	def packetLoop(self) -> None:
		'''Processes all recieved packets'''
		while not self.quit:
			rawPacket = self.recievedPackets.get()
			self.handlePacket(rawPacket)
			self.recievedPackets.task_done()

	def initialHandshake(self, conn: socket.socket) -> Optional[Exception]:
		conn.send(S2CHandshake().encode())
		try:
			checkPacket = conn.recv(8)
		except ConnectionResetError:
			print(f"Error during response from closed peer.")
			conn.close()
			return ConnectionError()

		if not checkPacket:
			print(f"No response to handshake from peer: {conn.getpeername()}")
			conn.send(S2CFailedHandshake().encode())
			time.sleep(0.1) # time for client to close on their end
			conn.close()
			return ConnectionError()
		
		if self.handlePacket(RawPacket(checkPacket, conn)) is not None:
			print(f"Handshake failed (incorrect data recieved) when connecting to peer: {conn.getpeername()}")
			conn.send(S2CFailedHandshake().encode())
			time.sleep(0.1) # time for client to close on their end
			conn.close()
			return ConnectionError()
		
		print(f"Connection established to peer: {conn.getpeername()}")

		self.onClientJoin(conn)

	def closeServer(self) -> None:
		self.quit = True
	
	def broadcast(self, packet: Packet) -> None:
		for c in self.openConnections:
			c.send(packet.encode())

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

	def onClientJoin(self, conn: socket.socket) -> None:
		self.game.addPlayer(CommonPlayer(random.randint(0, 1500), random.randint(0, 800)))
		# need to remove players on client disconnect

		self.broadcast(S2CPlayers(self.game.players))

	def mainLoop(self) -> None:
		'''Handles main game logic separate from network events'''
		while not self.quit:
			self.game.update()
			
			time.sleep(0.1) # if packets sent too fast, packets get combined and corrupted

			self.broadcast(S2CPlayers(self.game.players))

	def consoleLoop(self) -> None:
		'''Handles server console commands'''
		while not self.quit:
			consoleInput: str = input().lower().strip()

			match consoleInput:
				case "q" | "quit":
					self.closeServer()
				case _:
					pass

	def handlePacket(self, rawPacket: RawPacket) -> Optional[Exception]:
		packetType: int = Packet.decodeID(rawPacket.data)

		match packetType:
			case packetIDs.C2S_HANDSHAKE:
				handshakePacket: C2SHandshake = C2SHandshake.decodeData(rawPacket.data)

				if not handshakePacket.isCorrect():
					print("Error during handshake")
					return ConnectionError()
			
			case packetIDs.C2S_PLAYER_REQUEST:
				rawPacket.sender.send(S2CPlayers(self.game.players).encode())

			case _:
				print(f"Unknown packet (ID: {packetType})")
				return ConnectionError()
