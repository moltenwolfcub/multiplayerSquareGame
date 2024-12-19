import pygame
import sys

from settings import Settings

class Game:

	def __init__(self) -> None:
		pygame.init()

		self.settings: Settings = Settings()

		self.screen: pygame.Surface = pygame.display.set_mode((self.settings.screenWidth, self.settings.screenHeight), pygame.RESIZABLE)

		self.virtualScreen: pygame.Surface = pygame.Surface((self.settings.screenVirtualWidth, self.settings.screenVirtualHeight))
		self.virtualScreenOffset: tuple[int,int] = (0, 0)

		pygame.display.set_caption("Squares")


	def run(self) -> None:
		while True:
			self._checkEvents()
			self._updateScreen()
	
	def _updateScreen(self) -> None:
		self.virtualScreen.fill(self.settings.colorBg)

		self.screen.fill(self.settings.colorScreenOverflow)
		self.screen.blit(self.virtualScreen, self.virtualScreenOffset)
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
			self.settings.screenVirtualHeight = newY
			self.settings.screenVirtualWidth = self.settings.screenAspectRatio * newY

			barWidth = newX-self.settings.screenVirtualWidth
			self.virtualScreenOffset = (barWidth/2, 0)
			
		else:
			self.settings.screenVirtualWidth = newX
			self.settings.screenVirtualHeight = newX / self.settings.screenAspectRatio
		
			barHeight = newY-self.settings.screenVirtualHeight
			self.virtualScreenOffset = (0, barHeight/2)

		self.virtualScreen: pygame.Surface = pygame.Surface((self.settings.screenVirtualWidth, self.settings.screenVirtualHeight))
	

	def exitGame(self) -> None:
		sys.exit()


if __name__ == '__main__':
	instance: Game = Game()
	instance.run()
