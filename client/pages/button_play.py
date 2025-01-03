from typing import Callable
import pygame
from client.settings import Settings
from common.data_types import Color, Vec2D


class PlayButton:

    def __init__(self) -> None:
        self.pos: Vec2D = Vec2D(556, 459)
        self.rect: pygame.Rect = pygame.Rect(self.pos.x, self.pos.y, 488, 154)

        self.alternate_color: bool = False

    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:

        # drop shadow

        # outline
        outline_color = Settings.color_menu_button_outline_alt if self.alternate_color else Settings.color_menu_button_outline
        self._draw_bevelled_rect(screen, scaler, self.rect, 28, outline_color)

        # block

        block_rect: pygame.Rect = pygame.Rect(self.rect.x+10, self.rect.y+10, self.rect.w-20, self.rect.h-20)
        self._draw_bevelled_rect(screen, scaler, block_rect, 20, Settings.color_menu_button)

        # border

        # text

    @staticmethod
    def _draw_bevelled_rect(screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect], rect: pygame.Rect, radius: int, color: Color) -> None:
        vertical: pygame.Rect = scaler(pygame.Rect(rect.x+radius, rect.y, rect.w - radius*2, rect.h))
        pygame.draw.rect(screen, color.to_tuple(), vertical)

        horizontal: pygame.Rect = scaler(pygame.Rect(rect.x, rect.y+radius, rect.w, rect.h - radius*2))
        pygame.draw.rect(screen, color.to_tuple(), horizontal)

        curve_tl: pygame.Rect = scaler(pygame.Rect(rect.x+radius, rect.y+radius, radius, radius))
        curve_tr: pygame.Rect = scaler(pygame.Rect(rect.x+rect.w-radius, rect.y+radius, radius, radius))
        curve_bl: pygame.Rect = scaler(pygame.Rect(rect.x+radius, rect.y+rect.h-radius, radius, radius))
        curve_br: pygame.Rect = scaler(pygame.Rect(rect.x+rect.w-radius, rect.y+rect.h-radius, radius, radius))

        pygame.draw.circle(screen, color.to_tuple(), curve_tl.topleft, curve_tl.w)
        pygame.draw.circle(screen, color.to_tuple(), curve_tr.topleft, curve_tr.w)
        pygame.draw.circle(screen, color.to_tuple(), curve_bl.topleft, curve_bl.w)
        pygame.draw.circle(screen, color.to_tuple(), curve_br.topleft, curve_br.w)
