from typing import override

from common import packetIDs
from common.packetBase import Packet

class C2SHandshake(Packet):
	EXPECTED_MSG = "pong"
	def __init__(self, msg: str = EXPECTED_MSG) -> None:
		super().__init__(packetIDs.C2S_HANDSHAKE)

		self.message: str = msg
	
	@override
	def encodeData(self) -> bytes:
		return self.message.encode("utf-8")

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'C2SHandshake':
		packetData = data[1:]

		msg = packetData.decode("utf-8")
		return C2SHandshake(msg)
	
	def isCorrect(self) -> bool:
		return self.message == self.EXPECTED_MSG

class C2SRequestPlayerList(Packet):
	def __init__(self) -> None:
		super().__init__(packetIDs.C2S_PLAYER_REQUEST)

	@override
	def encodeData(self) -> bytes:
		return bytes()

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'C2SRequestPlayerList':
		return C2SRequestPlayerList()
