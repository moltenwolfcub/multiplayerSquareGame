import _thread
import sys

import pygame

from client import keybinds
from client.network import Network
from client.player import ClientPlayer
from client.settings import Settings
from common.c2sPackets import C2SRequestPlayerList


class Game:

	def __init__(self, port: int) -> None:
		pygame.init()

		self.settings: Settings = Settings()
		
		self.initialise_network(port)

		# region SCREEN-SETUP

		# Physical screen	-> Actual window on screen
		# Virtual screen	-> Subwindow in between black bars
		# Screen			-> constant 1600 x 900 screen
		# 
		# Screen is scaled to virtual screen and virtual screen is drawn
		# onto the physical one

		self.physical_screen: pygame.Surface = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE)
		pygame.display.set_caption("Squares")

		self.virtual_screen_width: int = self.settings.screen_width
		self.virtual_screen_height: int = self.settings.screen_height

		# this is the virtual screen
		self.screen: pygame.Surface = pygame.Surface((self.virtual_screen_width, self.virtual_screen_height))
		self.screen_offset: tuple[int,int] = (0, 0)

		# endregion

		self.players: list[ClientPlayer] = []
		self.network.send(C2SRequestPlayerList())

		self.movement_codes: list[int] = [0, 0, 0, 0]
		self.movement_codes_dirty: bool = False

		self.quit = False

	def initialise_network(self, port: int) -> None:
		self.network = Network(self, port)
		self.network.connect()

		_thread.start_new_thread(self.network.packet_loop, ())
		_thread.start_new_thread(self.network.read_loop, ())


	def run(self) -> None:
		while not self.quit:
			self._check_events()
			self.network.send_updates()
			self._update_screen()

		sys.exit()
	
	def _update_screen(self) -> None:
		# all coordinates are in the 1600 x 900 screen and scaled from there when drawing
		def scaler(r: pygame.Rect) -> pygame.Rect:
			'''Scales any rects from 1600 x 900 space to virtualScreen space'''

			scale_amount: float = self.virtual_screen_width / self.settings.screen_width
			return pygame.Rect(
				r.x * scale_amount,
				r.y * scale_amount,
				r.w * scale_amount,
				r.h * scale_amount,
			)


		self.screen.fill(self.settings.color_bg.to_tuple())

		for player in self.players:
			player.draw(scaler)

		self.physical_screen.fill(self.settings.color_screen_overflow.to_tuple())
		self.physical_screen.blit(self.screen, self.screen_offset)
		pygame.display.flip()

	def _check_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.exit_game()

			elif event.type == pygame.KEYDOWN:
				self._check_keydown_events(event)
			elif event.type == pygame.KEYUP:
				self._check_keyup_events(event)
			elif event.type == pygame.WINDOWRESIZED:
				self._resize_screen(event)
				   
	def _check_keydown_events(self, event: pygame.event.Event) -> None:
		match event.key:
			case keybinds.EXIT:
				self.exit_game()

			case keybinds.MOV_UP:
				self.movement_codes[0] = 1
				self.movement_codes_dirty = True
			case keybinds.MOV_DOWN:
				self.movement_codes[1] = 1
				self.movement_codes_dirty = True
			case keybinds.MOV_LEFT:
				self.movement_codes[2] = 1
				self.movement_codes_dirty = True
			case keybinds.MOV_RIGHT:
				self.movement_codes[3] = 1
				self.movement_codes_dirty = True

			case _:
				pass

	def _check_keyup_events(self, event: pygame.event.Event) -> None:
		match event.key:
			case keybinds.MOV_UP:
				self.movement_codes[0] = 0
				self.movement_codes_dirty = True
			case keybinds.MOV_DOWN:
				self.movement_codes[1] = 0
				self.movement_codes_dirty = True
			case keybinds.MOV_LEFT:
				self.movement_codes[2] = 0
				self.movement_codes_dirty = True
			case keybinds.MOV_RIGHT:
				self.movement_codes[3] = 0
				self.movement_codes_dirty = True

			case _:
				pass
	
	def _resize_screen(self, event: pygame.event.Event) -> None:
		newx, newy = event.x, event.y
		aspectRatio = newx / newy

		# more -> vertical bars
		# less -> horizontal bars
		if aspectRatio > self.settings.screen_aspect_ratio:
			self.virtual_screen_height = newy
			self.virtual_screen_width = self.settings.screen_aspect_ratio * newy

			bar_width = newx-self.virtual_screen_width
			self.screen_offset = (bar_width/2, 0)
			
		else:
			self.virtual_screen_width = newx
			self.virtual_screen_height = newx / self.settings.screen_aspect_ratio
		
			bar_height = newy-self.virtual_screen_height
			self.screen_offset = (0, bar_height/2)

		self.screen: pygame.Surface = pygame.Surface((self.virtual_screen_width, self.virtual_screen_height))


	def exit_game(self) -> None:
		self.network.close_connection()
		self.quit = True

