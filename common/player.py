
from common.dataTypes import Vec2D


class CommonPlayer:
	ENCODED_SIZE: int = 4

	def __init__(self, id: int, pos: Vec2D) -> None:

		self.id = id

		self.pos = pos

	def encode(self) -> bytes:
		b = self.pos.x.to_bytes(2)
		b += self.pos.y.to_bytes(2)

		return b

	@staticmethod
	def decode(bytes: bytes) -> 'CommonPlayer':
		x = int.from_bytes(bytes[:2])
		y = int.from_bytes(bytes[2:])

		return CommonPlayer(-1, Vec2D(x, y))
	
	def __str__(self) -> str:
		return f"Player[id= {self.id}, pos= {self.pos}]"

