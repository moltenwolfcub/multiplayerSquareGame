import queue
import socket
import sys
from typing import TYPE_CHECKING, Optional

from client.player import ClientPlayer
from common import packetIDs
from common.c2sPackets import C2SHandshake, C2SMovementUpdate
from common.dataTypes import Vec2D
from common.packetBase import Packet
from common.packetHeader import PacketHeader
from common.s2cPackets import S2CHandshake, S2CPlayers

if TYPE_CHECKING:
	from client.main import Game

class Network:
	def __init__(self, game: 'Game', port: int) -> None:
		self.game = game

		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server: str = "127.0.0.1"
		self.port: int = port

		self.recievedPackets: queue.Queue[bytes] = queue.Queue()
		self.quit: bool = False

	def connect(self) -> None:
		self.client.connect((self.server, self.port))
		recieved = self.recv()

		if recieved is None:
			print("No handshake sent from server")
			self.closeConnection()
		
		elif self.handlePacket(recieved) is not None:
			print("Handshake failed (incorrect data recieved) when connecting to server")
			# probably should send back a failure packet but cba rn
			self.closeConnection()
		
		if self.quit:
			sys.exit()

		self.send(C2SHandshake())
		print("Successfully established connection to server")
	
	def send(self, packet: Packet) -> None:
		# print(packet.encode())
		PacketHeader.sendPacket(self.client, packet)

	def recv(self) -> Optional[bytes]:
		header = self.client.recv(PacketHeader.HEADER_SIZE)
		if not header:
			return None

		packetSize = PacketHeader.getPacketsize(header)

		rawPacket = self.client.recv(packetSize)
		if not rawPacket:
			return None
		
		return rawPacket

	def readLoop(self) -> None:
		while not self.quit:
			try:
				rawPacket = self.recv()

				if rawPacket is None:
					print("Disconnected")
					self.closeConnection()
					break

				self.recievedPackets.put(rawPacket)

			except OSError as e:
				if e.errno == 9:
					print("Disconnected")
					self.closeConnection()
					break
				else:
					raise e

			except Exception as e:
				print("Network Error: ", e)
				self.closeConnection()
				break

	def packetLoop(self) -> None:
		while not self.quit:
			rawPacket = self.recievedPackets.get()
			self.handlePacket(rawPacket)
			self.recievedPackets.task_done()

	def closeConnection(self) -> None:
		try:
			self.client.close()
		except:
			pass

		self.quit = True

#===== ABOVE THIS LINE IS NETWORK INTERNALS =====

	def handlePacket(self, rawPacket: bytes) -> Optional[Exception]:
		packetType = Packet.decodeID(rawPacket)

		match packetType:
			case packetIDs.S2C_HANDSHAKE:
				handShakePacket: S2CHandshake = S2CHandshake.decodeData(rawPacket)

				if not handShakePacket.isCorrect():
					print("Error during handshake")
					return ConnectionError()
				
			case packetIDs.S2C_HANDSHAKE_FAIL:
				print("Server error during handshake. Aborting")
				self.closeConnection()
			
			case packetIDs.S2C_PLAYERS:
				playersPacket: S2CPlayers = S2CPlayers.decodeData(rawPacket)
				
				clientPlayers: list[ClientPlayer] = []

				for commonPlayer in playersPacket.players:
					clientPlayers.append(ClientPlayer.fromCommon(commonPlayer, self.game))
				
				self.game.players = clientPlayers
				
				# print("PLAYERS")
				# for p in playersPacket.players:
				# 	print(f"- {p}")

			case _:
				print(f"Unknown packet (ID: {packetType})")
				return ConnectionError()
	
	def sendUpdates(self) -> None:
		if self.game.movementCodesDirty:
			dx = self.game.movementCodes[3] - self.game.movementCodes[2]
			dy = self.game.movementCodes[1] - self.game.movementCodes[0]
			self.send(C2SMovementUpdate(Vec2D(dx,dy)))

			self.game.movementCodesDirty = False
