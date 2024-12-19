import pygame
from typing import (
	TYPE_CHECKING,
	Callable
)

if TYPE_CHECKING:
	from main import Game

class Player:
	'''General player for rendering local and remote players'''
	
	def __init__(self, game: 'Game', x: int, y: int) -> None:
		self.game: Game = game

		self.pos: tuple[int, int] = (x, y)
		
		self.size: int = self.game.settings.playerSize
		self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

	def draw(self, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
		drawRect = scaler(self.rect)

		pygame.draw.rect(self.game.screen, (200, 20, 20), drawRect)
