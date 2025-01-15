import sys

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing import Any, Callable, TypeVar

    F = TypeVar("F", bound=Callable[..., Any])
    def override(method: F, /) -> F:
        return method

from common import packet_ids
from common.data_types import Vec2D
from common.packet_base import Packet


class C2SHandshake(Packet):
    EXPECTED_MSG = "pong"
    def __init__(self, msg: str = EXPECTED_MSG) -> None:
        super().__init__(packet_ids.C2S_HANDSHAKE)

        self.message: str = msg
    
    @override
    def encode_data(self) -> bytes:
        return self.message.encode("utf-8")

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'C2SHandshake':
        packet_data = data[packet_ids.packet_id_size:]

        msg = packet_data.decode("utf-8")
        return C2SHandshake(msg)
    
    def isCorrect(self) -> bool:
        return self.message == self.EXPECTED_MSG

class C2SRequestPlayerList(Packet):
    def __init__(self) -> None:
        super().__init__(packet_ids.C2S_PLAYER_REQUEST)

    @override
    def encode_data(self) -> bytes:
        return bytes()

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'C2SRequestPlayerList':
        return C2SRequestPlayerList()

class C2SMovementUpdate(Packet):
    def __init__(self, mov_dir: Vec2D) -> None:
        super().__init__(packet_ids.C2S_MOVEMENT_UPDATE)

        self.mov_dir = mov_dir
    
    @override
    def encode_data(self) -> bytes:
        # 2 bits for each delta. b'0000xxyy'
        bdx: int = 0
        if self.mov_dir.x == 0:
            bdx = 0b00
        elif self.mov_dir.x == 1:
            bdx = 0b01
        elif self.mov_dir.x == -1:
            bdx = 0b10
        else:
            print(f"error encoding movement bytes. unknown movement Direction x-value {self.mov_dir.x}")

        bdy: int = 0
        if self.mov_dir.y == 0:
            bdy = 0b00
        elif self.mov_dir.y == 1:
            bdy = 0b01
        elif self.mov_dir.y ==  -1:
            bdy = 0b10
        else:
            print(f"error encoding movement bytes. unknown movement Direction y-value {self.mov_dir.y}")
        
        encoded = (bdx << 2) + bdy
        return encoded.to_bytes(1, byteorder="big")

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'C2SMovementUpdate':
        packet_data = data[packet_ids.packet_id_size:]

        packed_deltas = int.from_bytes(packet_data, byteorder="big")
        packed_dx = packed_deltas >> 2
        packed_dy = packed_deltas & 0b0011

        dx = 0
        if packed_dx == 0b00:
            dx = 0
        elif packed_dx == 0b01:
            dx = 1
        elif packed_dx == 0b10:
            dx = -1
        else:
            print(f"error decoding movement bytes. unknown movement Direction x-value {packed_dx}")

        dy = 0
        if packed_dy == 0b00:
            dy = 0
        elif packed_dy == 0b01:
            dy = 1
        elif packed_dy == 0b10:
            dy = -1
        else:
            print(f"error decoding movement bytes. unknown movement Direction y-value {packed_dy}")
        
        return C2SMovementUpdate(Vec2D(dx,dy))

class C2SCreateBullet(Packet):

    def __init__(self, angle: int) -> None:
        super().__init__(packet_ids.C2S_CREATE_BULLET)

        self.angle: int = angle

    @override
    def encode_data(self) -> bytes:
        b = self.angle.to_bytes(2, byteorder="big")

        return b

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'C2SCreateBullet':
        packet_data = data[packet_ids.packet_id_size:]

        angle: int = int.from_bytes(packet_data, byteorder="big")

        return C2SCreateBullet(angle)

class C2SClientDisconnect(Packet):
    def __init__(self) -> None:
        super().__init__(packet_ids.C2S_CLIENT_DISCONNECT)

    @override
    def encode_data(self) -> bytes:
        return bytes()

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'C2SRequestPlayerList':
        return C2SRequestPlayerList()
