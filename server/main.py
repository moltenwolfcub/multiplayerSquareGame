import _thread
import queue
import random
import socket
import sys
import time
from typing import Optional

from common import packetIDs
from common.c2sPackets import C2SHandshake, C2SMovementUpdate
from common.dataTypes import Vec2D
from common.packetBase import Packet
from common.packetHeader import PacketHeader
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

		self.openConnections: dict[socket.socket, int] = {}

		self.game: GameData = GameData(self)

	def start(self) -> None:
		try:
			self.socket.bind((self.server, self.port))
		except socket.error as e:
			print(e)
			self.closeServer()
			return
		
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
		
		self.onClientJoin(conn)

		while not self.quit:
			try:
				rawPacket = self.recv(conn)
				if rawPacket is None:
					self.closeConnection(conn)
					break

				self.recievedPackets.put(RawPacket(rawPacket, conn))

			except ConnectionResetError:
				self.closeConnection(conn)
				break

			except Exception as e:
				self.closeConnection(conn)
				print("Network Error: ", e)
				break
		
		# once players are properly linked to clients change to a client disconnect message
		print(f"Lost connection to peer")
		self.onClientDisconnect(conn)
	
	def packetLoop(self) -> None:
		'''Processes all recieved packets'''
		while not self.quit:
			rawPacket = self.recievedPackets.get()
			self.handlePacket(rawPacket)
			self.recievedPackets.task_done()

	def initialHandshake(self, conn: socket.socket) -> Optional[Exception]:
		PacketHeader.sendPacket(conn, S2CHandshake())
		try:
			checkPacket = self.recv(conn)
		except ConnectionResetError:
			print(f"Error during response from closed peer.")
			self.closeConnection(conn)
			return ConnectionError()

		if checkPacket is None:
			print(f"No response to handshake from peer: {conn.getpeername()}")
			PacketHeader.sendPacket(conn, S2CFailedHandshake())
			time.sleep(0.1) # time for client to close on their end
			self.closeConnection(conn)
			return ConnectionError()
		
		if self.handlePacket(RawPacket(checkPacket, conn)) is not None:
			print(f"Handshake failed (incorrect data recieved) when connecting to peer: {conn.getpeername()}")
			PacketHeader.sendPacket(conn, S2CFailedHandshake())
			time.sleep(0.1) # time for client to close on their end
			self.closeConnection(conn)
			return ConnectionError()
		
		print(f"Connection established to peer: {conn.getpeername()}")

	def closeServer(self) -> None:
		self.quit = True

	def closeConnection(self, conn: socket.socket) -> None:
		try:
			conn.close()
		except:
			print("Error while closing connection")
		
	def getFreeID(self) -> int:
		id = 0
		while True:
			if list(self.openConnections.values()).count(id) == 0:
				return id
			id += 1

	def broadcast(self, packet: Packet) -> None:
		for c in self.openConnections:
			try:
				PacketHeader.sendPacket(c, packet)
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

		packetSize = PacketHeader.getPacketsize(header)

		rawPacket = conn.recv(packetSize)
		if not rawPacket:
			return None
		
		# printBytes(rawPacket)
		return rawPacket

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

	def onClientJoin(self, conn: socket.socket) -> None:
		id = self.getFreeID()
		self.openConnections[conn] = id

		self.game.addPlayer(CommonPlayer(
			id,
			Vec2D(random.randint(0, 1500), random.randint(0, 800)),
			Vec2D(0,0)
		))

		self.broadcast(S2CPlayers(self.game.players))
	
	def onClientDisconnect(self, conn: socket.socket) -> None:
		id = self.openConnections.pop(conn, None)

		if id is None:
			return # connection was never in list

		self.game.removePlayer(id)

		self.broadcast(S2CPlayers(self.game.players))

	def mainLoop(self) -> None:
		'''Handles main game logic separate from network events'''
		while not self.quit:
			tickStart = time.perf_counter_ns()

			self.game.update()

			tickStop = time.perf_counter_ns()
			timeRemainingNS = self.game.settings.tickTimeNS - (tickStop-tickStart)

			if timeRemainingNS > 0:
				time.sleep(timeRemainingNS//1_000_000_000)

	def consoleLoop(self) -> None:
		'''Handles server console commands'''
		while not self.quit:
			consoleInput: str = input().lower().strip()

			match consoleInput:
				case "q" | "quit":
					self.closeServer()

				case "p" | "players":
					print("PLAYERS:")
					for p in self.game.players:
						print(f"- {p}")

					if len(self.game.players) == 0:
						print("empty")

				case "c" | "connections":
					print("CONNECTIONS:")
					for c in self.openConnections:
						id = self.openConnections[c]
						print(f"- {id}: {c}")

					if len(self.game.players) == 0:
						print("empty")

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
				PacketHeader.sendPacket(rawPacket.sender, S2CPlayers(self.game.players))
			
			case packetIDs.C2S_MOVEMENT_UPDATE:
				movementPacket: C2SMovementUpdate = C2SMovementUpdate.decodeData(rawPacket.data)

				player = self.game.getPlayer(self.openConnections[rawPacket.sender])
				if player is None:
					print(f"Error! No player assosiated with connection: {rawPacket.sender}")
					return LookupError()
				
				player.movDir = movementPacket.movDir

			case _:
				print(f"Unknown packet (ID: {packetType})")
				return ConnectionError()
