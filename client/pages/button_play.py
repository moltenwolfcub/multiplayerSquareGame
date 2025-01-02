from typing import Callable
import pygame
from client.settings import Settings
from common.data_types import Vec2D


class PlayButton:

    def __init__(self) -> None:
        self.pos: Vec2D = Vec2D(556, 459)
        self.rect: pygame.Rect = pygame.Rect(self.pos.x, self.pos.y, 488, 154)

        self.alternate_color: bool = False

    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        draw_rect = scaler(self.rect)

        # drop shadow

        # block
        pygame.draw.rect(screen, Settings.color_menu_button.to_tuple(), draw_rect)
        
        # outline

        # border

        # text

