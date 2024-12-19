import pygame
import typing

if typing.TYPE_CHECKING:
	from main import Game

class Player:
	'''General player for rendering local and remote players'''
	
	def __init__(self, game: 'Game', x: int, y: int) -> None:
		self.game: Game = game

		self.pos: tuple[int, int] = (x, y)
		
		self.size: int = 25
		self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

	def draw(self) -> None:
		pygame.draw.rect(self.game.screen, (200, 20, 20), self.rect)
