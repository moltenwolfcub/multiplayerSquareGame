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

		self.connect()

	def connect(self) -> None:
		self.client.connect((self.server, self.port))
		recieved = self.client.recv(8)

		if not recieved:
			print("No handshake sent from server")
			self.client.close()
			sys.exit()
		
		if self.handlePacket(recieved) is not None:
			print("Handshake failed (incorrect data recieved) when connecting to server")
			# probably should send back a failure packet but cba rn
			self.client.close()
			sys.exit()
		
		self.client.send(C2SHandshake("").encode())

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
				self.client.close()
				sys.exit()

			case _:
				print(f"Unknown packet (ID: {packetType})")
				return ConnectionError()

n = Network()
input() # to stop auto-closing program
