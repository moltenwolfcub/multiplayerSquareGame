import _thread
import math
import sys

import pygame

from client import keybinds
from client.bullet import ClientBullet
from client.network import Network
from client.player import ClientPlayer
from client.settings import Settings
from common.c2s_packets import C2SRequestPlayerList
from common.data_types import Vec2D


class Game:

    def __init__(self, port: int) -> None:
        pygame.init()

        self.settings: Settings = Settings()
        
        self.initialise_network(port)

        # region SCREEN-SETUP

        # Physical screen    -> Actual window on screen
        # Virtual screen    -> Subwindow in between black bars
        # Screen            -> constant 1600 x 900 screen
        # 
        # Screen is scaled to virtual screen and virtual screen is drawn
        # onto the physical one

        self.physical_screen: pygame.Surface = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Squares")

        self.virtual_screen_width: int = self.settings.screen_width
        self.virtual_screen_height: int = self.settings.screen_height

        # this is the virtual screen
        self.screen: pygame.Surface = pygame.Surface((self.virtual_screen_width, self.virtual_screen_height))
        self.screen_offset: Vec2D = Vec2D(0, 0)

        # endregion

        self.this_player_id: int = -1

        self.players: list[ClientPlayer] = []
        self.network.send(C2SRequestPlayerList())

        self.bullets: list[ClientBullet] = []

        self.movement_codes: list[int] = [0, 0, 0, 0]
        self.movement_codes_dirty: bool = False

        self.shoot_angle: float = -1

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

        for bullet in self.bullets:
            bullet.draw(scaler)


        self.physical_screen.fill(self.settings.color_screen_overflow.to_tuple())
        self.physical_screen.blit(self.screen, self.screen_offset.to_tuple())
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
            
            case keybinds.SHOOT:
                self.shoot()

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
        aspect_ratio = newx / newy

        # more -> vertical bars
        # less -> horizontal bars
        if aspect_ratio > self.settings.screen_aspect_ratio:
            self.virtual_screen_height = newy
            self.virtual_screen_width = self.settings.screen_aspect_ratio * newy

            bar_width = newx-self.virtual_screen_width
            self.screen_offset = Vec2D(bar_width/2, 0)
            
        else:
            self.virtual_screen_width = newx
            self.virtual_screen_height = newx / self.settings.screen_aspect_ratio
        
            bar_height = newy-self.virtual_screen_height
            self.screen_offset = Vec2D(0, bar_height/2)

        self.screen: pygame.Surface = pygame.Surface((self.virtual_screen_width, self.virtual_screen_height))


    def screen_to_world(self, screen: Vec2D) -> Vec2D:
        scalar: float = self.virtual_screen_width / self.settings.screen_width

        screen = screen - self.screen_offset
        world_vec: Vec2D = screen/scalar

        return world_vec

    def get_this_player(self) -> ClientPlayer:
        return self.players[self.this_player_id]

    def exit_game(self) -> None:
        self.network.close_connection()
        self.quit = True
    
    def shoot(self) -> None:
        if not pygame.mouse.get_focused():
            return # mouse not on screen
        
        raw_mouse_pos: Vec2D = Vec2D.from_tuple(pygame.mouse.get_pos())
        mouse_pos: Vec2D = self.screen_to_world(raw_mouse_pos)
        
        player_pos: Vec2D = self.get_this_player().pos

        shoot_vec: Vec2D = mouse_pos-player_pos
        x, y = shoot_vec.x, shoot_vec.y

        if x == y == 0:
            return # no direction because mouse exactly on player
        
        alpha: float
        if x == 0 or y == 0:
            alpha = 0
        else:
            abs_x, abs_y = abs(x), abs(y)

            if x/abs_x == y/abs_y:
                alpha = math.atan(abs_y / abs_x)
            else:
                alpha = math.atan(abs_x / abs_y)
        
        alpha = math.degrees(alpha)
        
        if x >= 0 and y < 0:
            self.shoot_angle = 0 + alpha
        elif x > 0 and y >= 0:
            self.shoot_angle = 90 + alpha
        elif x <= 0 and y > 0:
            self.shoot_angle = 180 + alpha
        elif x < 0 and y <= 0:
            self.shoot_angle = 270 + alpha

