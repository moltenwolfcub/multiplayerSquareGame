import socket
import _thread
import sys

class Server:

	def __init__(self) -> None:
		self.server: str = "127.0.0.1"
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def start(self) -> None:
		try:
			self.socket.bind((self.server, 0))
		except socket.error as e:
			print(e)
			self.closeServer()
		
		self.socket.listen()
		print(f"Server started on port {self.socket.getsockname()[1]}")

		_thread.start_new_thread(self.mainLoop, ())
		_thread.start_new_thread(self.packetLoop, ())
		_thread.start_new_thread(self.acceptLoop, ())

		input()


	def acceptLoop(self) -> None:
		'''Handles accepting new clients'''
		while True:
			conn, addr = self.socket.accept()
			print(f"Connected to: {addr}")

			_thread.start_new_thread(self.readLoop, (conn,))
	
	def readLoop(self, conn: socket.socket) -> None:
		'''One per client to store received packets for later processing'''

		while True:
			try:
				data = conn.recv(2048)

				if not data:
					print("Disconnected")
					break
			except:
				break
		
		print(f"Lost connection to peer: {conn.getpeername()}")
		conn.close()
	
	def packetLoop(self) -> None:
		'''Processes all recieved packets'''
		while True:
			pass

	def mainLoop(self) -> None:
		'''Handles main game logic separate from network events'''
		while True:
			pass


	def closeServer(self) -> None:
		sys.exit()

if __name__ == '__main__':
	s: Server = Server()
	s.start()
