from typing import override

from common import packetIDs
from common.packetBase import Packet

EXPECTED_MSG = "pong"

class C2SHandhsake(Packet):
	def __init__(self, msg: str = EXPECTED_MSG) -> None:
		super().__init__(packetIDs.C2S_HANDSHAKE)

		self.message: str = msg
	
	@override
	def encodeData(self) -> bytes:
		return self.message.encode("utf-8")

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'C2SHandhsake':
		packetData = data[1:]

		msg = packetData.decode("utf-8")
		return C2SHandhsake(msg)
	
	def isCorrect(self) -> bool:
		return self.message == EXPECTED_MSG
