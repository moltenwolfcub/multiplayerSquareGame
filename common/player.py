
from common.dataTypes import Vec2D


class CommonPlayer:
	ENCODED_SIZE: int = 4

	def __init__(self, id: int, pos: Vec2D, movDir: Vec2D) -> None:

		self.id = id

		self.pos = pos
		self.movDir = movDir # 1, 0, -1

	def encode(self) -> bytes:
		b = self.pos.x.to_bytes(2)
		b += self.pos.y.to_bytes(2)

		return b

	@staticmethod
	def decode(bytes: bytes) -> 'CommonPlayer':
		x = int.from_bytes(bytes[:2])
		y = int.from_bytes(bytes[2:])

		return CommonPlayer(id=-1, pos=Vec2D(x, y), movDir= Vec2D(0,0))
	
	def __str__(self) -> str:
		return f"Player[id= {self.id}, pos= {self.pos}, movDir= {self.movDir}]"
	
	def __eq__(self, value: object) -> bool:
		if not isinstance(value, CommonPlayer):
			return False

		if value.pos != self.pos:
			return False
		
		return True
