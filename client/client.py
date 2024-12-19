import pygame
import sys

from settings import Settings

class Game:

	def __init__(self) -> None:
		pygame.init()

		self.settings = Settings()

		self.screen = pygame.display.set_mode((self.settings.screenWidth, self.settings.screenHeight), pygame.RESIZABLE)
		pygame.display.set_caption("Squares")

	def run(self) -> None:
		while True:
			self._checkEvents()
			self._updateScreen()
	
	def _updateScreen(self) -> None:
		self.screen.fill(self.settings.colorBg)

		pygame.display.flip()

	def _checkEvents(self) -> None:
		"""Respond to keypresses and mouse events"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.exitGame()

			elif event.type == pygame.KEYDOWN:
				self._checkKeydownEvents(event)
			elif event.type == pygame.KEYUP:
				self._checkKeyupEvents(event)
			elif event.type == pygame.VIDEORESIZE:
				self._resizeScreen(event)
				   
	def _checkKeydownEvents(self, event) -> None:
		"""Respond to key presses."""
		if event.key == pygame.K_ESCAPE:
			self.exitGame()

	def _checkKeyupEvents(self, event) -> None:
		"""Respond to key releases"""
		pass
	
	def _resizeScreen(self, event) -> None:
		pass
			
	def exitGame(self) -> None:
		sys.exit()


if __name__ == '__main__':
	instance = Game()
	instance.run()
