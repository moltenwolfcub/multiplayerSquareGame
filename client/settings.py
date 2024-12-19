
type color = tuple[int,int,int]

class Settings:

	def __init__(self) -> None:

		# screen
		self.screenWidth: int = 1600
		self.screenHeight: int = 900
		
		self.screenAspectRatio: float = self.screenWidth / self.screenHeight

		# colors
		self.colorScreenOverflow: color = (0, 0, 0)
		self.colorBg: color = (63, 63, 63)

