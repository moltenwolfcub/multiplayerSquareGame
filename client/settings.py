
from common.dataTypes import Color


class Settings:

	def __init__(self) -> None:

		# screen
		self.screenWidth: int = 1600
		self.screenHeight: int = 900
		
		self.screenAspectRatio: float = self.screenWidth / self.screenHeight

		# colors
		self.colorScreenOverflow: Color = Color(0, 0, 0)
		self.colorBg: Color = Color(63, 63, 63)

		# player
		self.playerRadius: int = 50
