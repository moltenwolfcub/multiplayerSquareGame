from typing import override

from common import packet_ids
from common.bullet import CommonBullet
from common.packet_base import Packet
from common.player import CommonPlayer


class S2CHandshake(Packet):
    EXPECTED_MSG: str = "ping"
    def __init__(self, msg: str = EXPECTED_MSG) -> None:
        super().__init__(packet_ids.S2C_HANDSHAKE)

        self.message: str = msg
    
    @override
    def encode_data(self) -> bytes:
        return self.message.encode("utf-8")

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'S2CHandshake':
        packet_data = data[packet_ids.packet_id_size:]

        msg = packet_data.decode("utf-8")
        return S2CHandshake(msg)
    
    def isCorrect(self) -> bool:
        return self.message == self.EXPECTED_MSG


class S2CFailedHandshake(Packet):
    def __init__(self) -> None:
        super().__init__(packet_ids.S2C_HANDSHAKE_FAIL)
    
    @override
    def encode_data(self) -> bytes:
        return bytes()

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'S2CHandshake':
        return S2CHandshake()


class S2CPlayers(Packet):
    def __init__(self, players: list[CommonPlayer]) -> None:
        super().__init__(packet_ids.S2C_PLAYERS)

        self.players = players

    @override
    def encode_data(self) -> bytes:
        b = bytes()
        for player in self.players:
            b += player.encode()
        
        return b

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'S2CPlayers':
        packet_data = data[packet_ids.packet_id_size:]

        player_list: list[CommonPlayer] = []

        players = [ packet_data[i:i+CommonPlayer.ENCODED_SIZE] for i in range(0, len(packet_data), CommonPlayer.ENCODED_SIZE) ]

        for p in players:
            if len(p) == 0:
                continue

            player = CommonPlayer.decode(p)

            player_list.append(player)

        return S2CPlayers(player_list)

class S2CBullets(Packet):

    def __init__(self, bullets: list[CommonBullet]) -> None:
        super().__init__(packet_ids.S2C_BULLETS)
        
        self.bullets = bullets

    @override
    def encode_data(self) -> bytes:
        b = bytes()
        for bullet in self.bullets:
            b += bullet.encode()
        
        return b
    
    @override
    @staticmethod
    def decode_data(data: bytes) -> 'S2CBullets':
        packet_data = data[packet_ids.packet_id_size:]

        bullet_list: list[CommonBullet] = []

        players = [ packet_data[i:i+CommonBullet.ENCODED_SIZE] for i in range(0, len(packet_data), CommonBullet.ENCODED_SIZE) ]

        for p in players:
            if len(p) == 0:
                continue

            bullet = CommonBullet.decode(p)

            bullet_list.append(bullet)

        return S2CBullets(bullet_list)

class S2CSendID(Packet):

    def __init__(self, id: int) -> None:
        super().__init__(packet_ids.S2C_SEND_ID)

        self.player_id: int = id
    
    @override
    def encode_data(self) -> bytes:
        return self.player_id.to_bytes(1)

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'S2CSendID':
        packet_data = data[packet_ids.packet_id_size:]

        player_id = int.from_bytes(packet_data)
        return S2CSendID(player_id)

class S2CDisconnectPlayer(Packet):
    KICKED = 0
    KILLED = 1

    def __init__(self, reason: int) -> None:
        super().__init__(packet_ids.S2C_PLAYER_DISCONNECT)

        self.reason: int = reason
    
    @override
    def encode_data(self) -> bytes:
        return self.reason.to_bytes(1)

    @override
    @staticmethod
    def decode_data(data: bytes) -> 'S2CDisconnectPlayer':
        packet_data = data[packet_ids.packet_id_size:]

        reason = int.from_bytes(packet_data)
        return S2CDisconnectPlayer(reason)
