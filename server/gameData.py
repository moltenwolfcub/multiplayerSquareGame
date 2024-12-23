from typing import TYPE_CHECKING, Optional

from common.dataTypes import Vec2D
from common.player import CommonPlayer
from common.s2cPackets import S2CPlayers
from server.settings import Settings

if TYPE_CHECKING:
	from server.main import Server

class GameData:
	def __init__(self, server: 'Server') -> None:
		self.server: Server = server

		self.settings: Settings = Settings()

		self.players: list[CommonPlayer] = []
	
	def update(self) -> None:
		
		playersDirty = False
		for player in self.players:
			if player.movDir.isNone():
				continue
			
			playersDirty = True
			newPos: Vec2D = player.pos + player.movDir * self.settings.playerSpeed

			player.pos.x = min(self.settings.worldWidth, max(0, newPos.x))
			player.pos.y = min(self.settings.worldHeight, max(0, newPos.y))

		if playersDirty:
			self.server.broadcast(S2CPlayers(self.players))

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
