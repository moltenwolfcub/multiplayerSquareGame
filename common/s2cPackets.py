from typing import override

import packetIDs
from packetBase import Packet

EXPECTED_MSG = "ping"

class S2CHandhsake(Packet):
	def __init__(self, msg: str = EXPECTED_MSG) -> None:
		super().__init__(packetIDs.S2C_HANDSHAKE)

		self.message: str = msg
	
	@override
	def encodeData(self) -> bytes:
		return self.message.encode("utf-8")

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'S2CHandhsake':
		packetData = data[1:]

		msg = packetData.decode("utf-8")
		return S2CHandhsake(msg)
	
	def isCorrect(self) -> bool:
		return self.message == EXPECTED_MSG
