
from common.player import Player


class Game:
	def __init__(self) -> None:
		self.players: list[Player] = [
			Player(100, 500)
		]
