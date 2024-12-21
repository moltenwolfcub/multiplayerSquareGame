
from common.player import CommonPlayer


class Game:
	def __init__(self) -> None:
		self.players: list[CommonPlayer] = [
			CommonPlayer(100, 500)
		]
