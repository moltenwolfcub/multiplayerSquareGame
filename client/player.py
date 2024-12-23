from typing import TYPE_CHECKING, Callable

import pygame

from common.dataTypes import Vec2D
from common.player import CommonPlayer

if TYPE_CHECKING:
	from client.main import Game

class ClientPlayer:
	'''General player for rendering local and remote players'''
	
	def __init__(self, game: 'Game', pos: Vec2D) -> None:
		self.game: Game = game

		self.pos: Vec2D = pos
		
		self.size: int = self.game.settings.playerSize
		self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

	def draw(self, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
		drawRect = scaler(self.rect)

		pygame.draw.rect(self.game.screen, (200, 20, 20), drawRect)
	
	@staticmethod
	def fromCommon(common: CommonPlayer, game: 'Game') -> 'ClientPlayer':
		return ClientPlayer(game, common.pos)

	def __str__(self) -> str:
		return f"Player[pos=({self.pos})]"
