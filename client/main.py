import sys

import pygame

from client import keybinds
from client.game import Game
from client.settings import Settings
from common.data_types import Vec2D


class Client:

    def __init__(self, port: int) -> None:
        pygame.init()

        self.settings: Settings = Settings()
        self.game: Game = Game(port, self.settings)

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

        self.quit = False


    def run(self) -> None:
        while not self.quit:
            self._check_events()
            self.game.network.send_updates()
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

        for bullet in self.game.bullets:
            bullet.draw(scaler=scaler, screen=self.screen)

        for player in self.game.players:
            player.draw(scaler=scaler, screen=self.screen)


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
                self.game.movement_codes[0] = 1
                self.game.movement_codes_dirty = True
            case keybinds.MOV_DOWN:
                self.game.movement_codes[1] = 1
                self.game.movement_codes_dirty = True
            case keybinds.MOV_LEFT:
                self.game.movement_codes[2] = 1
                self.game.movement_codes_dirty = True
            case keybinds.MOV_RIGHT:
                self.game.movement_codes[3] = 1
                self.game.movement_codes_dirty = True
            
            case keybinds.SHOOT:
                if not pygame.mouse.get_focused():
                    return # mouse not on screen
                
                raw_mouse_pos: Vec2D = Vec2D.from_tuple(pygame.mouse.get_pos())
                mouse_pos: Vec2D = self.screen_to_world(raw_mouse_pos)
                self.game.shoot(mouse_pos)

            case _:
                pass

    def _check_keyup_events(self, event: pygame.event.Event) -> None:
        match event.key:
            case keybinds.MOV_UP:
                self.game.movement_codes[0] = 0
                self.game.movement_codes_dirty = True
            case keybinds.MOV_DOWN:
                self.game.movement_codes[1] = 0
                self.game.movement_codes_dirty = True
            case keybinds.MOV_LEFT:
                self.game.movement_codes[2] = 0
                self.game.movement_codes_dirty = True
            case keybinds.MOV_RIGHT:
                self.game.movement_codes[3] = 0
                self.game.movement_codes_dirty = True

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

    def exit_game(self) -> None:
        self.game.network.close_connection()
        self.quit = True

