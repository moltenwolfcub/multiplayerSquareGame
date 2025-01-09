from common.data_types import Rect, Vec2D


class Settings:
    tps: int = 60
    tick_time_ns: int = 1_000_000_000 // tps

    # worldSize
    world_width: int = 1600
    world_height: int = 900

    world_rect: Rect = Rect(Vec2D(0, 0), Vec2D(world_width, world_height))

    # player
    player_radius: int = 50
    player_speed: int = 3

    #bullet
    bullet_speed: int = 10
