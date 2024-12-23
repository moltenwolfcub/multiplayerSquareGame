
from common.player import CommonPlayer


class GameData:
	def __init__(self) -> None:
		self.players: list[CommonPlayer] = []
	
	def update(self) -> None:
		pass

	def addPlayer(self, player: CommonPlayer) -> None:
		self.players.append(player)
	
	def removePlayer(self, playerId: int) -> None:
		for player in self.players:
			if player.id == playerId:
				self.players.remove(player)
				return # if more than 1 player with same ID something very wrong
