import sys

import pygame

from client.pages import page_ids
from client.pages.page_game import GamePage
from client.pages.page_menu import MenuPage
from client.pages.page import Page
from client.settings import Settings
from common.data_types import Vec2D


class Client:

    def __init__(self, port: int) -> None:
        pygame.init()

        self.port: int = port # temporary until implement a page to join server
        
        self.page: Page = MenuPage(page_changer=self.change_page, mouse_getter=self.get_mouse_pos)

        # region SCREEN-SETUP

        # Physical screen    -> Actual window on screen
        # Virtual screen    -> Subwindow in between black bars
        # Screen            -> constant 1600 x 900 screen
        # 
        # Screen is scaled to virtual screen and virtual screen is drawn
        # onto the physical one

        self.physical_screen: pygame.Surface = pygame.display.set_mode((Settings.screen_width, Settings.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Squares")

        self.virtual_screen_width: int = Settings.screen_width
        self.virtual_screen_height: int = Settings.screen_height

        # this is the virtual screen
        self.screen: pygame.Surface = pygame.Surface((self.virtual_screen_width, self.virtual_screen_height))
        self.screen_offset: Vec2D = Vec2D(0, 0)

        # endregion

        self.quit = False


    def run(self) -> None:
        while not self.quit:
            self._check_events()
            self.page.update()
            self._update_screen()

        sys.exit()
    
    def _update_screen(self) -> None:
        # all coordinates are in the 1600 x 900 screen and scaled from there when drawing
        def scaler(r: pygame.Rect) -> pygame.Rect:
            '''Scales any rects from 1600 x 900 space to virtualScreen space'''

            scale_amount: float = self.virtual_screen_width / Settings.screen_width
            return pygame.Rect(
                r.x * scale_amount,
                r.y * scale_amount,
                r.w * scale_amount,
                r.h * scale_amount,
            )
        

        self.page.draw(self.screen, scaler)


        self.physical_screen.fill(Settings.color_screen_overflow.to_tuple())
        self.physical_screen.blit(self.screen, self.screen_offset.to_tuple())
        pygame.display.flip()

    def _check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()
                continue
            elif event.type == pygame.WINDOWRESIZED:
                self._resize_screen(event)
                continue
            
            feedback_code = self.page.check_event(event)
            match feedback_code:
                case 1:
                    self.exit_game()
                case 0 | _:
                    pass
    
    def _resize_screen(self, event: pygame.event.Event) -> None:
        newx, newy = event.x, event.y
        aspect_ratio = newx / newy

        # more -> vertical bars
        # less -> horizontal bars
        if aspect_ratio > Settings.screen_aspect_ratio:
            self.virtual_screen_height = newy
            self.virtual_screen_width = Settings.screen_aspect_ratio * newy

            bar_width = newx-self.virtual_screen_width
            self.screen_offset = Vec2D(bar_width/2, 0)
            
        else:
            self.virtual_screen_width = newx
            self.virtual_screen_height = newx / Settings.screen_aspect_ratio
        
            bar_height = newy-self.virtual_screen_height
            self.screen_offset = Vec2D(0, bar_height/2)

        self.screen: pygame.Surface = pygame.Surface((self.virtual_screen_width, self.virtual_screen_height))

        self.page.on_resize(self.virtual_screen_width / Settings.screen_width)


    def screen_to_world(self, screen: Vec2D) -> Vec2D:
        scalar: float = self.virtual_screen_width / Settings.screen_width

        screen = screen - self.screen_offset
        world_vec: Vec2D = screen/scalar

        return world_vec
    
    def get_mouse_pos(self) -> Vec2D:
        raw_mouse_pos: Vec2D = Vec2D.from_tuple(pygame.mouse.get_pos())
        mouse_pos: Vec2D = self.screen_to_world(raw_mouse_pos)
        return mouse_pos

    def exit_game(self) -> None:
        self.page.close()
        self.quit = True
    
    def change_page(self, page_id: int) -> None:
        match page_id:
            case page_ids.PAGE_MENU:
                self.page.close()

                self.page = MenuPage(page_changer=self.change_page, mouse_getter=self.get_mouse_pos)
            case page_ids.PAGE_GAME:
                self.page.close()
                
                self.page = GamePage(port=self.port, mouse_getter=self.get_mouse_pos)
            case _:
                print(f"Error: Unknown page ID({page_id}). Staying on old page")
