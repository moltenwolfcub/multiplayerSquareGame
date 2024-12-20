from client.main import Game
from server.main import Server


def main() -> None:
	SERVER: bool = True
	if SERVER:
		s: Server = Server()
		s.start()
	
	else:
		g: Game = Game()
		g.run()


if __name__ == '__main__':
	main()
