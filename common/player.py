from common.data_types import Color, Vec2D


class CommonPlayer:
    ENCODED_SIZE: int = 7

    def __init__(self, id: int, pos: Vec2D, mov_dir: Vec2D, color: Color) -> None:

        self.id = id

        self.pos = pos
        self.mov_dir = mov_dir # 1, 0, -1

        self.color = color

    def encode(self) -> bytes:
        b = self.pos.x.to_bytes(2)
        b += self.pos.y.to_bytes(2)

        b += self.color.r.to_bytes(1)
        b += self.color.g.to_bytes(1)
        b += self.color.b.to_bytes(1)

        return b

    @staticmethod
    def decode(bytes: bytes) -> 'CommonPlayer':
        x = int.from_bytes(bytes[:2])
        y = int.from_bytes(bytes[2:4])

        r = int.from_bytes(bytes[4:5])
        g = int.from_bytes(bytes[5:6])
        b = int.from_bytes(bytes[6:7])

        return CommonPlayer(id=-1, pos=Vec2D(x, y), mov_dir=Vec2D(0,0), color=Color(r,g,b))
    
    def __str__(self) -> str:
        return f"Player[id= {self.id}, pos= {self.pos}, movDir= {self.mov_dir}]"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CommonPlayer):
            return False

        if other.pos != self.pos:
            return False
    
        if other.color != self.color:
            return False
        
        return True
