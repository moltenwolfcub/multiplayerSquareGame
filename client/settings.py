
from common.data_types import Color


class Settings:

    def __init__(self) -> None:

        # screen
        self.screen_width: int = 1600
        self.screen_height: int = 900
        
        self.screen_aspect_ratio: float = self.screen_width / self.screen_height

        # server
        self.tps: int = 20
        self.tick_time_ns: int = 1_000_000_000 // self.tps

        # colors
        self.color_screen_overflow: Color = Color(0, 0, 0)
        self.color_bg: Color = Color(63, 63, 63)

        # player
        self.player_radius: int = 50

        # bullet
        self.bullet_speed: int = 10
