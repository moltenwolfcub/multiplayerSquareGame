import socket
from common.packetBase import Packet

class PacketHeader:
	HEADER_SIZE: int = 2

	def __init__(self, packet: Packet) -> None:
		self.payload: bytes = packet.encode()

		self.packetSize: int = len(self.payload)
	
	def send(self, conn: socket.socket) -> None:
		header: bytes = self.packetSize.to_bytes(PacketHeader.HEADER_SIZE)

		conn.send(header + self.payload)
	
	@staticmethod
	def sendBytes(conn: socket.socket, data: bytes) -> None:
		header: bytes = len(data).to_bytes(PacketHeader.HEADER_SIZE)

		conn.send(header + data)

	@staticmethod
	def sendPacket(conn: socket.socket, packet: Packet) -> None:
		data: bytes = packet.encode()

		header: bytes = len(data).to_bytes(PacketHeader.HEADER_SIZE)

		conn.send(header + data)

	@staticmethod
	def getPacketsize(header: bytes) -> int:
		return int.from_bytes(header)
