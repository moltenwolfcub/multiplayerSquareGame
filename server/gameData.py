
from common.player import CommonPlayer


class GameData:
	def __init__(self) -> None:
		self.players: list[CommonPlayer] = [
			CommonPlayer(100, 500),
			CommonPlayer(400, 750)
		]
	
	def update(self) -> None:
		self.players[0].pos = (
			self.players[0].pos[0] + 1,
			self.players[0].pos[1]
		)
