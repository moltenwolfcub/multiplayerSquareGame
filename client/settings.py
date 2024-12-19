
type color = tuple[int,int,int]

class Settings:

	def __init__(self) -> None:

		# screen
		self.screenPhysicalWidth: int = 1600
		self.screenPhysicalHeight: int = 900
		
		self.screenAspectRatio: float = self.screenPhysicalWidth / self.screenPhysicalHeight

		# colors
		self.colorScreenOverflow: color = (0, 0, 0)
		self.colorBg: color = (63, 63, 63)

