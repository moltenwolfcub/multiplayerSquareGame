from typing import Callable, override

import pygame
from client.pages.page import Page


class MenuPage(Page):
    
    def __init__(self) -> None:
        pass


    @override
    def check_event(self, event: pygame.event.Event) -> int:
        return 0

    @override
    def update(self) -> None:
        pass

    @override
    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        pass
    
    @override
    def close(self) -> None:
        pass
