
class Settings:

	def __init__(self) -> None:
		self.tps: int = 20
		self.tickTimeNS: int = 1_000_000_000 // self.tps

		# worldSize
		self.worldWidth: int = 1600
		self.worldHeight: int = 900

		# player
		self.playerSize: int = 100
		self.playerSpeed: int = 3
