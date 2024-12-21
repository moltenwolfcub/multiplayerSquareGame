import _thread
import sys

import pygame

from client.network import Network
from client.player import Player
from client.settings import Settings
from common.c2sPackets import C2SRequestPlayerList


class Game:

	def __init__(self, port: int) -> None:
		pygame.init()

		self.initialiseNetwork(port)

		self.settings: Settings = Settings()

		# region SCREEN-SETUP

		# Physical screen	-> Actual window on screen
		# Virtual screen	-> Subwindow in between black bars
		# Screen			-> constant 1600 x 900 screen
		# 
		# Screen is scaled to virtual screen and virtual screen is drawn
		# onto the physical one

		self.physicalScreen: pygame.Surface = pygame.display.set_mode((self.settings.screenWidth, self.settings.screenHeight), pygame.RESIZABLE)
		pygame.display.set_caption("Squares")

		self.virtualScreenWidth: int = self.settings.screenWidth
		self.virtualScreenHeight: int = self.settings.screenHeight

		# this is the virtual screen
		self.screen: pygame.Surface = pygame.Surface((self.virtualScreenWidth, self.virtualScreenHeight))
		self.screenOffset: tuple[int,int] = (0, 0)

		# endregion

		self.players: list[Player] = []
		self.network.send(C2SRequestPlayerList())

		self.quit = False

	def initialiseNetwork(self, port: int) -> None:
		self.network = Network(self, port)
		self.network.connect()

		_thread.start_new_thread(self.network.packetLoop, ())
		_thread.start_new_thread(self.network.readLoop, ())


	def run(self) -> None:
		while not self.quit:
			self._checkEvents()
			self._updateScreen()

		sys.exit()
	
	def _updateScreen(self) -> None:
		# all coordinates are in the 1600 x 900 screen and scaled from there when drawing
		def scaler(r: pygame.Rect) -> pygame.Rect:
			'''Scales any rects from 1600 x 900 space to virtualScreen space'''

			scaleAmount: float = self.virtualScreenWidth / self.settings.screenWidth
			return pygame.Rect(
				r.x * scaleAmount,
				r.y * scaleAmount,
				r.w * scaleAmount,
				r.h * scaleAmount,
			)


		self.screen.fill(self.settings.colorBg)

		for player in self.players:
			player.draw(scaler)

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
			self.virtualScreenHeight = newY
			self.virtualScreenWidth = self.settings.screenAspectRatio * newY

			barWidth = newX-self.virtualScreenWidth
			self.screenOffset = (barWidth/2, 0)
			
		else:
			self.virtualScreenWidth = newX
			self.virtualScreenHeight = newX / self.settings.screenAspectRatio
		
			barHeight = newY-self.virtualScreenHeight
			self.screenOffset = (0, barHeight/2)

		self.screen: pygame.Surface = pygame.Surface((self.virtualScreenWidth, self.virtualScreenHeight))


	def exitGame(self) -> None:
		self.network.closeConnection()
		self.quit = True

