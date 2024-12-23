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

		self.openConnections: list[socket.socket] = []

		self.game: GameData = GameData()

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
		
		self.openConnections.append(conn)

		while not self.quit:
			try:
				rawPacket = self.recv(conn)
				if rawPacket is None:
					self.closeConnection(conn)
					print("Disconnected")
					break

				self.recievedPackets.put(RawPacket(rawPacket, conn))

			except ConnectionResetError:
				self.closeConnection(conn)
				print("Disconnected")
				break

			except Exception as e:
				self.closeConnection(conn)
				print("Network Error: ", e)
				break
		
		# once players are properly linked to clients change to a client disconnect message
		print(f"Lost connection to peer")
	
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

		self.onClientJoin(conn)

	def closeServer(self) -> None:
		self.quit = True

	def closeConnection(self, conn: socket.socket) -> None:
		try:
			conn.close()
		except:
			print("Error while closing connection")

		try:
			self.openConnections.remove(conn)
		except ValueError:
			pass # connection wasn't even in list yet so can't be removed

	def broadcast(self, packet: Packet) -> None:
		for c in self.openConnections:
			try:
				PacketHeader.sendPacket(c, packet)
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
		
		return rawPacket

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

	def onClientJoin(self, conn: socket.socket) -> None:
		self.game.addPlayer(CommonPlayer(random.randint(0, 1500), random.randint(0, 800)))
		# need to remove players on client disconnect

		self.broadcast(S2CPlayers(self.game.players))

	def mainLoop(self) -> None:
		'''Handles main game logic separate from network events'''
		while not self.quit:
			self.game.update()

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
				PacketHeader.sendPacket(rawPacket.sender, S2CPlayers(self.game.players))

			case _:
				print(f"Unknown packet (ID: {packetType})")
				return ConnectionError()
