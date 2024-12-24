import math
from dataclasses import dataclass


@dataclass
class Vec2D:
    x: int
    y: int

    def __mul__(self, scalar: int) -> 'Vec2D':
        return Vec2D(
            self.x * scalar,
            self.y * scalar,
        )
    
    def __rmul__(self, scalar: int) -> 'Vec2D':
        return self.__mul__(scalar)
    
    def __add__(self, other: 'Vec2D') -> 'Vec2D':
        return Vec2D(
            self.x + other.x,
            self.y + other.y,
        )
    
    def isNone(self) -> bool:
        return self.x == 0 and self.y == 0
    
    def __floordiv__(self, divisor: float) -> 'Vec2D':
        return Vec2D(
            int(self.x / divisor),
            int(self.y / divisor),
        )
    
    def __truediv__(self, divisor: float) -> 'Vec2D':

        newx = 0
        newy = 0

        if self.x < 0:
            newx = math.floor(self.x / divisor)
        elif self.x > 0:
            newx = math.ceil(self.x / divisor)

        if self.y < 0:
            newy = math.floor(self.y / divisor)
        elif self.y > 0:
            newy = math.ceil(self.y / divisor)

        return Vec2D(
            math.ceil(newx),
            math.ceil(newy),
        )

@dataclass
class Color:
    r: int
    g: int
    b: int

    def to_tuple(self) -> tuple[int,int,int]:
        return (self.r, self.g, self.b)
