from typing import Callable, override

import pygame
from client.game import Game
from client.pages import page_ids
from client.pages.button import Button
from client.pages.page import Page
from client.settings import Settings
from common.data_types import Vec2D


class DeathPage(Page):
    
    def __init__(self, game: Game) -> None:
        self.game: Game = game
        
        self.respawn_button: Button = Button("Respawn", Vec2D(556, 459), Vec2D(488, 154))
        self.exit_button: Button = Button("Exit", Vec2D(556, 559), Vec2D(488, 154))

    @override
    def check_event(self, event: pygame.event.Event) -> int:
        return 0

    @override
    def update(self) -> None:
        pass

    @override
    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        screen.fill(Settings.color_bg.to_tuple())

        self.respawn_button.draw(screen, scaler)
        self.exit_button.draw(screen, scaler)
    
    @override
    def close(self, next_page: int) -> None:
        if next_page != page_ids.PAGE_GAME:
            self.game.close()

    @override
    def on_resize(self, scale_factor: float) -> None:
        pass
