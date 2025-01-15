import sys
from typing import Callable

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing import Any, TypeVar

    F = TypeVar("F", bound=Callable[..., Any])
    def override(method: F, /) -> F:
        return method

import pygame

from client.game import Game
from client.pages.page import Page
from client.settings import Settings
from common.data_types import Vec2D


class GamePage(Page):
    
    def __init__(self, page_changer: Callable[[int], None], port: int, mouse_getter: Callable[[], Vec2D]) -> None:
        self.game: Game = Game(page_changer, port, mouse_getter)


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
        self.game.close()

    @override
    def on_resize(self, scale_factor: float) -> None:
        pass
