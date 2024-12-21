
class Player:
	ENCODED_SIZE: int = 4

	def __init__(self, x: int = 0, y: int = 0) -> None:

		self.pos: tuple[int, int] = (x, y)

	def encode(self) -> bytes:
		b = self.pos[0].to_bytes(2)
		b += self.pos[1].to_bytes(2)

		return b

	@staticmethod
	def decode(bytes: bytes) -> 'Player':
		x = int.from_bytes(bytes[:2])
		y = int.from_bytes(bytes[2:])

		return Player(x, y)

