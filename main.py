import argparse

from client.main import Game
from server.main import Server


def main() -> None:

	args = parse_args()

	# defaults to client
	server = False # true for server false for client
	if args.side == "server":
		server = True

	if server:
		port: int = 0
		if args.port is not None:
			port = args.port

		s: Server = Server(port)
		s.start()
	else:
		if args.port is None:
			print("No port provided to connect to")
		
		else:
			g: Game = Game(args.port)
			g.run()

def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		prog = "Squares game",
		description = "A simple 2d muliplayer game written in python with pygame"
	)
	parser.add_argument("-s", "-side", choices=["client", "server"], dest="side")
	parser.add_argument("-p", "-port", type=int, dest="port")
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	main()
