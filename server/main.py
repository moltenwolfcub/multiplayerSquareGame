import queue
import socket
import _thread
import sys
from typing import Optional

from common import packetIDs
from common.c2sPackets import C2SHandhsake
from common.packetBase import Packet
from common.s2cPackets import S2CFailedHandhsake, S2CHandhsake

class Server:

	def __init__(self, port: int = 0) -> None:
		self.server: str = "127.0.0.1"
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.port: int = port

		self.recievedPackets: queue.Queue[bytes] = queue.Queue()

	def start(self) -> None:
		try:
			self.socket.bind((self.server, self.port))
		except socket.error as e:
			print(e)
			self.closeServer()
		
		self.socket.listen()
		print(f"Server started on port {self.socket.getsockname()[1]}")

		_thread.start_new_thread(self.mainLoop, ())
		_thread.start_new_thread(self.packetLoop, ())
		_thread.start_new_thread(self.acceptLoop, ())
		
		while True: pass


	def acceptLoop(self) -> None:
		'''Handles accepting new clients'''
		while True:
			conn, addr = self.socket.accept()
			print(f"Connecting to: {addr}")

			_thread.start_new_thread(self.readLoop, (conn,))
	
	def readLoop(self, conn: socket.socket) -> None:
		'''One per client to store received packets for later processing'''
		if self.initialHandshake(conn) is not None:
			return

		while True:
			try:
				rawData = conn.recv(2048)

				if not rawData:
					print("Disconnected")
					break

				self.recievedPackets.put(rawData)

			except:
				break
		
		print(f"Lost connection to peer: {conn.getpeername()}")
		conn.close()
	
	def packetLoop(self) -> None:
		'''Processes all recieved packets'''
		while True:
			rawPacket = self.recievedPackets.get()
			self.handlePacket(rawPacket)
			self.recievedPackets.task_done()

	def mainLoop(self) -> None:
		'''Handles main game logic separate from network events'''
		while True:
			pass


	def handlePacket(self, rawPacket: bytes) -> Optional[Exception]:
		packetType = Packet.decodeID(rawPacket)

		match packetType:
			case packetIDs.C2S_HANDSHAKE:
				packet: C2SHandhsake = C2SHandhsake.decodeData(rawPacket)

				if not packet.isCorrect():
					print("Error during handshake")
					return ConnectionError()
			case _:
				print(f"Unknown packet (ID: {packetType})")
				return ConnectionError()

	def initialHandshake(self, conn: socket.socket) -> Optional[Exception]:
		conn.send(S2CHandhsake().encode())
		checkPacket = conn.recv(8)

		if not checkPacket:
			print(f"No response to handshake from peer: {conn.getpeername()}")
			conn.send(S2CFailedHandhsake().encode())
			conn.close()
			return ConnectionError()
		
		if self.handlePacket(checkPacket) is not None:
			print(f"Handshake failed when connecting to peer: {conn.getpeername()}")
			conn.send(S2CFailedHandhsake().encode())
			conn.close()
			return ConnectionError()
		
		print(f"Connection established to peer: {conn.getpeername()}")

	def closeServer(self) -> None:
		sys.exit()

if __name__ == '__main__':
	s: Server = Server()
	s.start()
