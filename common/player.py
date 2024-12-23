
class CommonPlayer:
	ENCODED_SIZE: int = 4

	def __init__(self, id: int, x: int = 0, y: int = 0) -> None:

		self.id = id

		self.x: int = x
		self.y: int = y

	def encode(self) -> bytes:
		b = self.x.to_bytes(2)
		b += self.y.to_bytes(2)

		return b

	@staticmethod
	def decode(bytes: bytes) -> 'CommonPlayer':
		x = int.from_bytes(bytes[:2])
		y = int.from_bytes(bytes[2:])

		return CommonPlayer(-1, x, y)
	
	def __str__(self) -> str:
		return f"Player[id= {self.id}, pos=({self.x}, {self.y})]"

