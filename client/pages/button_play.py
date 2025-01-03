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

        # drop shadow

        # outline
        outline_color = Settings.color_menu_button_outline_alt if self.alternate_color else Settings.color_menu_button_outline

        vertical_outline_rect: pygame.Rect = scaler(pygame.Rect(self.rect.x+28, self.rect.y, self.rect.w-56, self.rect.h))
        pygame.draw.rect(screen, outline_color.to_tuple(), vertical_outline_rect)

        horizontal_outline_rect: pygame.Rect = scaler(pygame.Rect(self.rect.x, self.rect.y+28, self.rect.w, self.rect.h-56))
        pygame.draw.rect(screen, outline_color.to_tuple(), horizontal_outline_rect)

        outline_curve_tl: pygame.Rect = scaler(pygame.Rect(self.rect.x+28, self.rect.y+28, 28, 28))
        outline_curve_tr: pygame.Rect = scaler(pygame.Rect(self.rect.x+self.rect.w-28, self.rect.y+28, 28, 28))
        outline_curve_bl: pygame.Rect = scaler(pygame.Rect(self.rect.x+28, self.rect.y+self.rect.h-28, 28, 28))
        outline_curve_br: pygame.Rect = scaler(pygame.Rect(self.rect.x+self.rect.w-28, self.rect.y+self.rect.h-28, 28, 28))

        pygame.draw.circle(screen, outline_color.to_tuple(), outline_curve_tl.topleft, outline_curve_tl.w)
        pygame.draw.circle(screen, outline_color.to_tuple(), outline_curve_tr.topleft, outline_curve_tr.w)
        pygame.draw.circle(screen, outline_color.to_tuple(), outline_curve_bl.topleft, outline_curve_bl.w)
        pygame.draw.circle(screen, outline_color.to_tuple(), outline_curve_br.topleft, outline_curve_br.w)

        # block
        vertical_block_rect: pygame.Rect = scaler(pygame.Rect(self.rect.x+10+20, self.rect.y+10, self.rect.w-20-40, self.rect.h-20))
        pygame.draw.rect(screen, Settings.color_menu_button.to_tuple(), vertical_block_rect)

        horizontal_block_rect: pygame.Rect = scaler(pygame.Rect(self.rect.x+10, self.rect.y+10+20, self.rect.w-20, self.rect.h-20-40))
        pygame.draw.rect(screen, Settings.color_menu_button.to_tuple(), horizontal_block_rect)

        block_curve_tl: pygame.Rect = scaler(pygame.Rect(self.rect.x+10+20, self.rect.y+10+20, 20, 20))
        block_curve_tr: pygame.Rect = scaler(pygame.Rect(self.rect.x+10+self.rect.w-40, self.rect.y+10+20, 20, 20))
        block_curve_bl: pygame.Rect = scaler(pygame.Rect(self.rect.x+10+20, self.rect.y+10+self.rect.h-40, 20, 20))
        block_curve_br: pygame.Rect = scaler(pygame.Rect(self.rect.x+10+self.rect.w-40, self.rect.y+10+self.rect.h-40, 20, 20))

        pygame.draw.circle(screen, Settings.color_menu_button.to_tuple(), block_curve_tl.topleft, block_curve_tl.w)
        pygame.draw.circle(screen, Settings.color_menu_button.to_tuple(), block_curve_tr.topleft, block_curve_tr.w)
        pygame.draw.circle(screen, Settings.color_menu_button.to_tuple(), block_curve_bl.topleft, block_curve_bl.w)
        pygame.draw.circle(screen, Settings.color_menu_button.to_tuple(), block_curve_br.topleft, block_curve_br.w)

        # border

        # text
