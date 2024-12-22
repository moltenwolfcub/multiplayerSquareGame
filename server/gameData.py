
from common.player import CommonPlayer


class GameData:
	def __init__(self) -> None:
		self.players: list[CommonPlayer] = []
	
	def update(self) -> None:
		pass

	def addPlayer(self, player: CommonPlayer) -> None:
		self.players.append(player)
