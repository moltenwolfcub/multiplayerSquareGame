from typing import override

from common import packet_ids
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
