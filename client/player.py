from typing import Callable

import pygame

from client.settings import Settings
from common.data_types import Color, Vec2D
from common.player import CommonPlayer

class ClientPlayer:
    '''General player for rendering local and remote players'''
    
    def __init__(self, id: int, pos: Vec2D, color: Color) -> None:
        self.id: int = id

        self.pos: Vec2D = pos
        self.color: Color = color
        
        self.radius: int = Settings.player_radius
        self.rect = pygame.Rect(self.pos.x-self.radius, self.pos.y-self.radius, self.radius*2, self.radius*2)

    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        draw_rect = scaler(self.rect)

        pygame.draw.rect(screen, self.color.to_tuple(), draw_rect)
    
    @staticmethod
    def from_common(common: CommonPlayer) -> 'ClientPlayer':
        return ClientPlayer(id=common.id, pos=common.pos, color=common.color)

    def __str__(self) -> str:
        return f"Player[id=({self.id}), pos=({self.pos}), color=({self.color})]"
