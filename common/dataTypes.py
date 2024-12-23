from dataclasses import dataclass


@dataclass
class Vec2D:
	x: int
	y: int

	def __mul__(self, scalar: int) -> 'Vec2D':
		return Vec2D(
			self.x * scalar,
			self.y * scalar
		)
	
	def __rmul__(self, scalar: int) -> 'Vec2D':
		return self.__mul__(scalar)
	
	def __add__(self, other: 'Vec2D') -> 'Vec2D':
		return Vec2D(
			self.x + other.x,
			self.y + other.y
		)
	
	def isNone(self) -> bool:
		return self.x == 0 and self.y == 0
