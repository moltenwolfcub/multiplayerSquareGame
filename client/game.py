import _thread
import math
from typing import Optional

from client.bullet import ClientBullet
from client.network import Network
from client.player import ClientPlayer
from client.settings import Settings
from common.c2s_packets import C2SRequestPlayerList
from common.data_types import Vec2D


class Game:
    
    def __init__(self, port: int, settings: Settings) -> None:
        self.settings: Settings = settings
        
        self.this_player_id: int = -1

        self.initialise_network(port)


        self.players: list[ClientPlayer] = []
        self.network.send(C2SRequestPlayerList())

        self.bullets: list[ClientBullet] = []

        self.movement_codes: list[int] = [0, 0, 0, 0]
        self.movement_codes_dirty: bool = False

        self.shoot_angle: float = -1

    def initialise_network(self, port: int) -> None:
        self.network = Network(self, port)
        self.network.connect()

        _thread.start_new_thread(self.network.packet_loop, ())
        _thread.start_new_thread(self.network.read_loop, ())

    def get_this_player(self) -> Optional[ClientPlayer]:
        if self.this_player_id == -1:
            print("ID hasn't been set yet")
            return None

        for p in self.players:
            if p.id == self.this_player_id:
                return p
        else:
            print("Couldn't find this_player")
            return None
    
    def shoot(self, mouse_pos: Vec2D) -> None:
        
        this_player: Optional[ClientPlayer] = self.get_this_player()
        if this_player is None:
            return # can't find self to shoot from
        player_pos = this_player.pos

        shoot_vec: Vec2D = mouse_pos-player_pos
        x, y = shoot_vec.x, shoot_vec.y

        if x == y == 0:
            return # no direction because mouse exactly on player
        
        alpha: float
        if x == 0 or y == 0:
            alpha = 0
        else:
            abs_x, abs_y = abs(x), abs(y)

            if x/abs_x == y/abs_y:
                alpha = math.atan(abs_y / abs_x)
            else:
                alpha = math.atan(abs_x / abs_y)
        
        alpha = math.degrees(alpha)
        
        if x >= 0 and y < 0:
            self.shoot_angle = 0 + alpha
        elif x > 0 and y >= 0:
            self.shoot_angle = 90 + alpha
        elif x <= 0 and y > 0:
            self.shoot_angle = 180 + alpha
        elif x < 0 and y <= 0:
            self.shoot_angle = 270 + alpha
