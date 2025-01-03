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

        translucent_outline: pygame.Surface = self._draw_bevelled_rect(scaler, self.rect, 28, outline_color)
        translucent_outline.set_alpha(65)
        screen.blit(translucent_outline, self.rect)

        outline_rect: pygame.Rect = pygame.Rect(self.rect.x+1, self.rect.y+1, self.rect.w-2, self.rect.h-2)
        screen.blit(self._draw_bevelled_rect(scaler, outline_rect, 28, outline_color), outline_rect.topleft)
        

        # block

        block_rect: pygame.Rect = pygame.Rect(self.rect.x+10, self.rect.y+10, self.rect.w-20, self.rect.h-20)
        screen.blit(self._draw_bevelled_rect(scaler, block_rect, 20, Settings.color_menu_button), block_rect)

        # border

        # text

    @staticmethod
    def _draw_bevelled_rect(scaler: Callable[[pygame.Rect], pygame.Rect], rect: pygame.Rect, radius: int, color: Color) -> pygame.Surface:
        surf: pygame.Surface = pygame.Surface(scaler(rect).size, pygame.SRCALPHA)

        vertical: pygame.Rect = scaler(pygame.Rect(radius, 0, rect.w - radius*2, rect.h))
        pygame.draw.rect(surf, color.to_tuple(), vertical)

        horizontal: pygame.Rect = scaler(pygame.Rect(0, radius, rect.w, rect.h - radius*2))
        pygame.draw.rect(surf, color.to_tuple(), horizontal)

        curve_tl: pygame.Rect = scaler(pygame.Rect(radius, radius, radius, radius))
        curve_tr: pygame.Rect = scaler(pygame.Rect(rect.w-radius, radius, radius, radius))
        curve_bl: pygame.Rect = scaler(pygame.Rect(radius, rect.h-radius, radius, radius))
        curve_br: pygame.Rect = scaler(pygame.Rect(rect.w-radius, rect.h-radius, radius, radius))

        pygame.draw.circle(surf, color.to_tuple(), curve_tl.topleft, curve_tl.w)
        pygame.draw.circle(surf, color.to_tuple(), curve_tr.topleft, curve_tr.w)
        pygame.draw.circle(surf, color.to_tuple(), curve_bl.topleft, curve_bl.w)
        pygame.draw.circle(surf, color.to_tuple(), curve_br.topleft, curve_br.w)

        return surf
