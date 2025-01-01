from abc import ABC, abstractmethod
from typing import Callable

import pygame


class Page(ABC):
    
    @abstractmethod
    def check_event(self, event: pygame.event.Event) -> int:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface, scaler: Callable[[pygame.Rect], pygame.Rect]) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
