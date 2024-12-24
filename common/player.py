from common.data_types import Color, Vec2D


class CommonPlayer:
    ENCODED_SIZE: int = 8

    def __init__(self, id: int, pos: Vec2D, mov_dir: Vec2D, color: Color) -> None:

        self.id = id

        self.pos = pos
        self.mov_dir = mov_dir # 1, 0, -1

        self.color = color

    def encode(self) -> bytes:
        b = bytes()

        b += self.id.to_bytes(1) # if ever get over 255 players at once then I'll improve it

        b += self.pos.x.to_bytes(2)
        b += self.pos.y.to_bytes(2)

        b += self.color.r.to_bytes(1)
        b += self.color.g.to_bytes(1)
        b += self.color.b.to_bytes(1)

        return b

    @staticmethod
    def decode(bytes: bytes) -> 'CommonPlayer':
        id = int.from_bytes(bytes[0:1])

        x = int.from_bytes(bytes[1:3])
        y = int.from_bytes(bytes[3:5])

        r = int.from_bytes(bytes[5:6])
        g = int.from_bytes(bytes[6:7])
        b = int.from_bytes(bytes[7:8])

        return CommonPlayer(id=id, pos=Vec2D(x, y), mov_dir=Vec2D(0,0), color=Color(r,g,b))
    
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
