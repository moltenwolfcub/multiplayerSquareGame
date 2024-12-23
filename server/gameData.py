
from typing import Optional
from common.player import CommonPlayer
from server.settings import Settings


class GameData:
	def __init__(self) -> None:
		self.settings: Settings = Settings()

		self.players: list[CommonPlayer] = []
	
	def update(self) -> None:
		pass

	def addPlayer(self, player: CommonPlayer) -> None:
		self.players.append(player)
	
	def removePlayer(self, playerId: int) -> None:
		player = self.getPlayer(playerId)
		if player:
			self.players.remove(player)
	
	def getPlayer(self, playerId: int) -> Optional[CommonPlayer]:
		for player in self.players:
			if player.id == playerId:
				return player # if more than 1 player with same ID something very wrong
		
		print(f"Couldn't find player with ID {playerId}")
		return None
