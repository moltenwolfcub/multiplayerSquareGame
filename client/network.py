import queue
import socket
import sys
from typing import Optional

from common import packetIDs
from common.c2sPackets import C2SHandshake
from common.packetBase import Packet
from common.s2cPackets import S2CHandshake


class Network:
	def __init__(self) -> None:
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server: str = "127.0.0.1"
		self.port: int = 5555

		self.recievedPackets: queue.Queue[bytes] = queue.Queue()
		self.quit: bool = False

	def connect(self) -> None:
		self.client.connect((self.server, self.port))
		recieved = self.client.recv(8)

		if not recieved:
			print("No handshake sent from server")
			self.closeConnection()
		
		elif self.handlePacket(recieved) is not None:
			print("Handshake failed (incorrect data recieved) when connecting to server")
			# probably should send back a failure packet but cba rn
			self.closeConnection()
		
		if self.quit:
			sys.exit()

		self.client.send(C2SHandshake().encode())
	
	def send(self, packet: Packet) -> None:
		self.client.send(packet.encode())

	def readLoop(self) -> None:
		while not self.quit:
			try:
				rawData = self.client.recv(2048)

				if not rawData:
					print("Disconnected")
					self.closeConnection()

				self.recievedPackets.put(rawData)

			except:
				break

	def packetLoop(self) -> None:
		while not self.quit:
			rawPacket = self.recievedPackets.get()
			self.handlePacket(rawPacket)
			self.recievedPackets.task_done()

	def handlePacket(self, rawPacket: bytes) -> Optional[Exception]:
		packetType = Packet.decodeID(rawPacket)

		match packetType:
			case packetIDs.S2C_HANDSHAKE:
				packet: S2CHandshake = S2CHandshake.decodeData(rawPacket)

				if not packet.isCorrect():
					print("Error during handshake")
					return ConnectionError()
				
			case packetIDs.S2C_HANDSHAKE_FAIL:
				print("Server error during handshake. Aborting")
				self.closeConnection()

			case _:
				print(f"Unknown packet (ID: {packetType})")
				return ConnectionError()

	def closeConnection(self) -> None:
		try:
			self.client.close()
		except:
			pass

		self.quit = True
