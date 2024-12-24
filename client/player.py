from typing import TYPE_CHECKING, Callable

import pygame

from common.data_types import Color, Vec2D
from common.player import CommonPlayer

if TYPE_CHECKING:
    from client.main import Game

class ClientPlayer:
    '''General player for rendering local and remote players'''
    
    def __init__(self, id: int, game: 'Game', pos: Vec2D, color: Color) -> None:
        self.game: Game = game

        self.id: int = id

        self.pos: Vec2D = pos

        self.color: Color = color
        
        self.radius: int = self.game.settings.player_radius
        self.rect = pygame.Rect(self.pos.x-self.radius, self.pos.y-self.radius, self.radius*2, self.radius*2)

    def draw(self, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        draw_rect = scaler(self.rect)

        pygame.draw.rect(self.game.screen, self.color.to_tuple(), draw_rect)
    
    @staticmethod
    def from_common(common: CommonPlayer, game: 'Game') -> 'ClientPlayer':
        return ClientPlayer(id=common.id, game=game, pos=common.pos, color=common.color)

    def __str__(self) -> str:
        return f"Player[id=({self.id}), pos=({self.pos}), color=({self.color})]"
