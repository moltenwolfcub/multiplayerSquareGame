import pygame
import sys

from player import Player
from settings import Settings

class Game:

	def __init__(self) -> None:
		pygame.init()

		self.settings: Settings = Settings()


		self.physicalScreen: pygame.Surface = pygame.display.set_mode((self.settings.screenPhysicalWidth, self.settings.screenPhysicalHeight), pygame.RESIZABLE)

		self.screenWidth: int = self.settings.screenPhysicalWidth
		self.screenHeight: int = self.settings.screenPhysicalHeight

		self.screen: pygame.Surface = pygame.Surface((self.screenWidth, self.screenHeight))
		self.screenOffset: tuple[int,int] = (0, 0)

		pygame.display.set_caption("Squares")


		self.localPlayer: Player = Player(self, 100, 100)


	def run(self) -> None:
		while True:
			self._checkEvents()
			self._updateScreen()
	
	def _updateScreen(self) -> None:
		# all coordinates are in the 1600x900 screen and scaled from there when drawing

		self.screen.fill(self.settings.colorBg)

		self.localPlayer.draw()


		self.physicalScreen.fill(self.settings.colorScreenOverflow)
		self.physicalScreen.blit(self.screen, self.screenOffset)
		pygame.display.flip()

	def _checkEvents(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.exitGame()

			elif event.type == pygame.KEYDOWN:
				self._checkKeydownEvents(event)
			elif event.type == pygame.KEYUP:
				self._checkKeyupEvents(event)
			elif event.type == pygame.WINDOWRESIZED:
				self._resizeScreen(event)
				   
	def _checkKeydownEvents(self, event: pygame.event.Event) -> None:
		if event.key == pygame.K_ESCAPE:
			self.exitGame()

	def _checkKeyupEvents(self, event: pygame.event.Event) -> None:
		pass
	
	def _resizeScreen(self, event: pygame.event.Event) -> None:
		newX, newY = event.x, event.y
		aspectRatio = newX / newY

		# more -> vertical bars
		# less -> horizontal bars
		if aspectRatio > self.settings.screenAspectRatio:
			self.screenHeight = newY
			self.screenWidth = self.settings.screenAspectRatio * newY

			barWidth = newX-self.screenWidth
			self.screenOffset = (barWidth/2, 0)
			
		else:
			self.screenWidth = newX
			self.screenHeight = newX / self.settings.screenAspectRatio
		
			barHeight = newY-self.screenHeight
			self.screenOffset = (0, barHeight/2)

		self.screen: pygame.Surface = pygame.Surface((self.screenWidth, self.screenHeight))


	def exitGame(self) -> None:
		sys.exit()


if __name__ == '__main__':
	instance: Game = Game()
	instance.run()
