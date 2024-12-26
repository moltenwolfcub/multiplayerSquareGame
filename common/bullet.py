
from common.data_types import Vec2D


class CommonBullet:
    ENCODED_SIZE: int = 4

    def __init__(self, pos: Vec2D, shoot_angle: int) -> None:

        self.pos = pos

        self.shoot_angle = shoot_angle

    def encode(self) -> bytes:
        b = self.pos.x.to_bytes(2)
        b += self.pos.y.to_bytes(2)

        return b

    @staticmethod
    def decode(bytes: bytes) -> 'CommonBullet':
        x = int.from_bytes(bytes[:2])
        y = int.from_bytes(bytes[2:4])

        return CommonBullet(pos=Vec2D(x, y), shoot_angle=-1)
    
    def __str__(self) -> str:
        return f"Bullet[pos= {self.pos}, shoot_angle= {self.shoot_angle}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CommonBullet):
            return False

        if other.pos != self.pos:
            return False
        
        return True
