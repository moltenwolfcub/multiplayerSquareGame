from typing import TYPE_CHECKING, Callable

import pygame

from common.bullet import CommonBullet
from common.data_types import Vec2D

if TYPE_CHECKING:
    from client.main import Game


class ClientBullet:

    def __init__(self, game: 'Game', pos: Vec2D) -> None:
        self.game: Game = game

        self.pos: Vec2D = pos

        self.radius: int = 10
        
        self.rect = pygame.Rect(self.pos.x-self.radius, self.pos.y-self.radius, self.radius*2, self.radius*2)

    def draw(self, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        draw_rect = scaler(self.rect)

        pygame.draw.circle(self.game.screen, (0, 0, 0), draw_rect.center, self.radius)
    
    @staticmethod
    def from_common(common: CommonBullet, game: 'Game') -> 'ClientBullet':
        return ClientBullet(game, common.pos)
