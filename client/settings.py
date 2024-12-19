

class Settings:

	def __init__(self) -> None:

		#screen
		self.screenWidth: int = 1600
		self.screenHeight: int = 900
		
		self.screenAspectRatio: float = self.screenWidth / self.screenHeight

		# colors
		self.colorBg: tuple[int, int, int] = (63, 63, 63)

