import _thread
import math
from typing import Callable, Optional

import pygame

from client import keybinds
from client.bullet import ClientBullet
from client.network import Network
from client.pages import page_ids
from client.player import ClientPlayer
from common.c2s_packets import C2SClientDisconnect, C2SCreateBullet, C2SMovementUpdate, C2SRequestPlayerList
from common.data_types import Vec2D


class Game:
    
    def __init__(self, page_changer: Callable[[int], None], port: int, mouse_getter: Callable[[], Vec2D]) -> None:
        self.page_changer: Callable[[int], None] = page_changer
        self.mouse_getter: Callable[[], Vec2D] = mouse_getter
        
        self.this_player_id: int = -1

        try:
            self.initialise_network(port)
            self.network_live: bool = True
        except ConnectionRefusedError:
            self.network_live: bool = False

        self.players: list[ClientPlayer] = []
        if self.network_live:
            self.network.send(C2SRequestPlayerList())

        self.bullets: list[ClientBullet] = []

        self.movement_codes: list[int] = [0, 0, 0, 0]
        self.movement_codes_dirty: bool = False

        self.shoot_angle: float = -1

        self.update_server_on_exit = True

    def initialise_network(self, port: int) -> None:
        self.network = Network(self, port)
        success: bool = self.network.connect()
        if not success:
            self.page_changer(page_ids.PAGE_MENU)
            return

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
        
    
    def tick(self) -> None:
        if not self.network_live:
            self.page_changer(page_ids.PAGE_MENU)
            return
        
        self.send_network_updates()
    
    def send_network_updates(self) -> None:
        if not self.network_live:
            return

        if self.movement_codes_dirty:
            dx = self.movement_codes[3] - self.movement_codes[2]
            dy = self.movement_codes[1] - self.movement_codes[0]
            self.network.send(C2SMovementUpdate(Vec2D(dx,dy)))

            self.movement_codes_dirty = False
        
        if self.shoot_angle != -1:
            rounded_angle: int = int(self.shoot_angle * 100) # fixed point decimal of angle 00000-36000

            self.network.send(C2SCreateBullet(rounded_angle))
            self.shoot_angle = -1


    def check_event(self, event: pygame.event.Event) -> int:
        if event.type == pygame.KEYDOWN:
            return self._check_keydown_events(event)
        elif event.type == pygame.KEYUP:
            return self._check_keyup_events(event)
        
        return 0
                   
    def _check_keydown_events(self, event: pygame.event.Event) -> int:
        if event.key == keybinds.EXIT:
            if self.network_live:
                self.page_changer(page_ids.PAGE_MENU)
            return 0

        elif event.key == keybinds.MOV_UP:
            self.movement_codes[0] = 1
            self.movement_codes_dirty = True
            return 0
        elif event.key == keybinds.MOV_DOWN:
            self.movement_codes[1] = 1
            self.movement_codes_dirty = True
            return 0
        elif event.key == keybinds.MOV_LEFT:
            self.movement_codes[2] = 1
            self.movement_codes_dirty = True
            return 0
        elif event.key == keybinds.MOV_RIGHT:
            self.movement_codes[3] = 1
            self.movement_codes_dirty = True
            return 0
        
        elif event.key == keybinds.SHOOT:
            self.shoot()
            return 0

        else:
            return 0

    def _check_keyup_events(self, event: pygame.event.Event) -> int:
        if event.key == keybinds.MOV_UP:
            self.movement_codes[0] = 0
            self.movement_codes_dirty = True
            return 0
        elif event.key == keybinds.MOV_DOWN:
            self.movement_codes[1] = 0
            self.movement_codes_dirty = True
            return 0
        elif event.key == keybinds.MOV_LEFT:
            self.movement_codes[2] = 0
            self.movement_codes_dirty = True
            return 0
        elif event.key == keybinds.MOV_RIGHT:
            self.movement_codes[3] = 0
            self.movement_codes_dirty = True
            return 0

        else:
            return 0
    

    def shoot(self) -> None:
        if not pygame.mouse.get_focused():
            return # mouse not on screen
        
        mouse_pos: Vec2D = self.mouse_getter()

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

    def close(self) -> None:
        if self.update_server_on_exit:
            self.network.send(C2SClientDisconnect())
        
        self.network.close_connection()
