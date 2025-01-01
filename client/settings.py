
from common.data_types import Color


class Settings:
    
    # screen
    screen_width: int = 1600
    screen_height: int = 900
    
    screen_aspect_ratio: float = screen_width / screen_height

    # colors
    color_screen_overflow: Color = Color(0, 0, 0)
    color_bg: Color = Color(63, 63, 63)

    color_title_bg: Color = Color(122, 122, 122)

    # player
    player_radius: int = 50

    # bullet
    bullet_speed: int = 10
