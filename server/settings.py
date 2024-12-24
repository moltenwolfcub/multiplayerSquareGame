
class Settings:

    def __init__(self) -> None:
        self.tps: int = 20
        self.tick_time_ns: int = 1_000_000_000 // self.tps

        # worldSize
        self.world_width: int = 1600
        self.world_height: int = 900

        # player
        self.player_radius: int = 50
        self.player_speed: int = 3
