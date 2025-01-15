
from typing import Optional
from common.data_types import Vec2D
from common.player import CommonPlayer


class CommonBullet:
    ENCODED_SIZE: int = 4

    def __init__(self, pos: Vec2D, shoot_angle: int, shooter: Optional[CommonPlayer] = None) -> None:
        self.owner: Optional[CommonPlayer] = shooter
        self.pos: Vec2D = pos
        self.shoot_angle: int = shoot_angle

    def encode(self) -> bytes:
        b = self.pos.x.to_bytes(2, byteorder="big")
        b += self.pos.y.to_bytes(2, byteorder="big")

        return b

    @staticmethod
    def decode(bytes: bytes) -> 'CommonBullet':
        x = int.from_bytes(bytes[:2], byteorder="big")
        y = int.from_bytes(bytes[2:4], byteorder="big")

        return CommonBullet(pos=Vec2D(x, y), shoot_angle=-1, shooter=None)
    
    def __str__(self) -> str:
        return f"Bullet[pos= {self.pos}, shoot_angle= {self.shoot_angle}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CommonBullet):
            return False

        if other.pos != self.pos:
            return False
        
        return True
