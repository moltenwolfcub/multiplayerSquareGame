import socket
from common.packetBase import Packet

class PacketHeader:
	HEADER_SIZE: int = 2

	def __init__(self, packet: Packet) -> None:
		self.payload: bytes = packet.encode()

		self.packet_size: int = len(self.payload)
	
	def send(self, conn: socket.socket) -> None:
		header: bytes = self.packet_size.to_bytes(PacketHeader.HEADER_SIZE)

		conn.send(header + self.payload)
	
	@staticmethod
	def sendBytes(conn: socket.socket, data: bytes) -> None:
		header: bytes = len(data).to_bytes(PacketHeader.HEADER_SIZE)

		conn.send(header + data)

	@staticmethod
	def send_packet(conn: socket.socket, packet: Packet) -> None:
		data: bytes = packet.encode()

		header: bytes = len(data).to_bytes(PacketHeader.HEADER_SIZE)

		conn.send(header + data)

	@staticmethod
	def get_packet_size(header: bytes) -> int:
		return int.from_bytes(header)
