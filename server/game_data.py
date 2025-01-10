import math
import random
from typing import TYPE_CHECKING, Optional

from common.bullet import CommonBullet
from common.data_types import Color, Rect, Vec2D
from common.player import CommonPlayer
from common.s2c_packets import S2CBullets, S2CDisconnectPlayer, S2CPlayers
from server.connection import Connection
from server.settings import Settings

if TYPE_CHECKING:
    from server.main import Server

class GameData:
    def __init__(self, server: 'Server') -> None:
        self.server: Server = server

        self.players: list[CommonPlayer] = []
        self.bullets: list[CommonBullet] = []
    
    def update(self) -> None:
        
        players_dirty = False
        for player in self.players:
            if player.mov_dir.is_none():
                continue
            
            players_dirty = True
            velocity: Vec2D = player.mov_dir * Settings.player_speed

            if player.mov_dir.x and player.mov_dir.y:
                velocity = velocity / 1.2

            new_pos = player.pos + velocity

            player.pos.x = min(Settings.world_width  - Settings.player_radius, max(Settings.player_radius, new_pos.x))
            player.pos.y = min(Settings.world_height - Settings.player_radius, max(Settings.player_radius, new_pos.y))
        
        bullet_dirty = False
        for bullet in self.bullets:

            # pol to cart
            shifted_angle: float = (bullet.shoot_angle / 100) - 90

            rawx = int(Settings.bullet_speed * math.cos(math.radians(shifted_angle)))
            rawy = int(Settings.bullet_speed * math.sin(math.radians(shifted_angle)))

            bullet.pos += Vec2D(rawx, rawy)

            bullet_dirty = True

            if not Settings.world_rect.contains(bullet.pos):
                self.bullets.remove(bullet)
                continue

        for player in self.players:
            player_rect: Rect = Rect(
                (player.pos-Vec2D(Settings.player_radius, Settings.player_radius)),
                (player.pos+Vec2D(Settings.player_radius, Settings.player_radius)),
            )
            conn: Connection = self.server.open_connections[player.id]

            gone_bullets: list[CommonBullet] = []

            for bullet in self.bullets:
                if player_rect.contains(bullet.pos):
                    self.server.send(conn, S2CDisconnectPlayer(S2CDisconnectPlayer.KILLED))
                    self.server.close_connection(conn)

                    gone_bullets.append(bullet)
                    bullet_dirty = True
                    players_dirty = True

            self.bullets = [b for b in self.bullets if b not in gone_bullets]                    

        if players_dirty:
            self.server.broadcast(S2CPlayers(self.players))
        
        if bullet_dirty:
            self.server.broadcast(S2CBullets(self.bullets))
        

    def add_player(self, player: CommonPlayer) -> None:
        self.players.append(player)
    
    def add_random_player(self, id: int) -> None:
        self.add_player(CommonPlayer(
            id,
            Vec2D(
                random.randint(Settings.player_radius, Settings.world_width-Settings.player_radius),
                random.randint(Settings.player_radius, Settings.world_height-Settings.player_radius)
            ),
            Vec2D(0,0),
            Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        ))
    
    def remove_player(self, player_id: int) -> None:
        player = self.get_player(player_id)
        if player:
            self.players.remove(player)
    
    def get_player(self, player_id: int) -> Optional[CommonPlayer]:
        for player in self.players:
            if player.id == player_id:
                return player # if more than 1 player with same ID something very wrong
        
        print(f"Couldn't find player with ID {player_id}")
        return None
