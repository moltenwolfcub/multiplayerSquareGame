
from common.data_types import Rect, Vec2D


class Settings:

    def __init__(self) -> None:
        self.tps: int = 60
        self.tick_time_ns: int = 1_000_000_000 // self.tps

        # worldSize
        self.world_width: int = 1600
        self.world_height: int = 900

        self.world_rect: Rect = Rect(Vec2D(0, 0), Vec2D(self.world_width, self.world_height))

        # player
        self.player_radius: int = 50
        self.player_speed: int = 3

        #bullet
        self.bullet_speed: int = 10
