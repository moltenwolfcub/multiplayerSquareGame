from typing import Callable, override

import pygame
from client.game import Game
from client.pages.page import Page
from client.settings import Settings
from common.data_types import Vec2D


class GamePage(Page):
    
    def __init__(self, port: int, mouse_getter: Callable[[], Vec2D]) -> None:
        self.game: Game = Game(port, mouse_getter)


    @override
    def check_event(self, event: pygame.event.Event) -> int:
        return self.game.check_event(event)

    @override
    def update(self) -> None:
        self.game.tick()

    @override
    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        screen.fill(Settings.color_bg.to_tuple())

        for bullet in self.game.bullets:
            bullet.draw(scaler=scaler, screen=screen)

        for player in self.game.players:
            player.draw(scaler=scaler, screen=screen)
    
    @override
    def close(self) -> None:
        self.game.network.close_connection()

    @override
    def on_resize(self, scale_factor: float) -> None:
        pass
