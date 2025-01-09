from typing import Callable

import pygame

from common.bullet import CommonBullet
from common.data_types import Vec2D


class ClientBullet:

    def __init__(self, pos: Vec2D) -> None:

        self.pos: Vec2D = pos

        self.radius: int = 10
        
        self.rect = pygame.Rect(self.pos.x-self.radius, self.pos.y-self.radius, self.radius*2, self.radius*2)

    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        draw_rect = scaler(self.rect)
        draw_radius = scaler(pygame.Rect(0,0,self.radius,self.radius))

        pygame.draw.circle(screen, (0, 0, 0), draw_rect.center, draw_radius.w)
    
    @staticmethod
    def from_common(common: CommonBullet) -> 'ClientBullet':
        return ClientBullet(pos= common.pos)
