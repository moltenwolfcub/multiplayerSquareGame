from typing import override

from common import packetIDs
from common.packetBase import Packet
from common.player import Player


class S2CHandshake(Packet):
	EXPECTED_MSG: str = "ping"
	def __init__(self, msg: str = EXPECTED_MSG) -> None:
		super().__init__(packetIDs.S2C_HANDSHAKE)

		self.message: str = msg
	
	@override
	def encodeData(self) -> bytes:
		return self.message.encode("utf-8")

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'S2CHandshake':
		packetData = data[1:]

		msg = packetData.decode("utf-8")
		return S2CHandshake(msg)
	
	def isCorrect(self) -> bool:
		return self.message == self.EXPECTED_MSG


class S2CFailedHandshake(Packet):
	def __init__(self) -> None:
		super().__init__(packetIDs.S2C_HANDSHAKE_FAIL)
	
	@override
	def encodeData(self) -> bytes:
		return bytes()

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'S2CHandshake':
		return S2CHandshake()


class S2CPlayers(Packet):
	def __init__(self, players: list[Player]) -> None:
		super().__init__(packetIDs.S2C_PLAYERS)

		self.players = players

	@override
	def encodeData(self) -> bytes:
		b = bytes()
		for player in self.players:
			b += player.encode()
		
		return b

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'S2CPlayers':
		packetData = data[1:]

		playerList: list[Player] = []

		players = [ packetData[i:i+Player.ENCODED_SIZE] for i in range(0, len(packetData), Player.ENCODED_SIZE) ]

		for p in players:
			if len(p) == 0:
				continue

			player = Player.decode(p)

			playerList.append(player)

		return S2CPlayers(playerList)
