from typing import override

from common import packetIDs
from common.dataTypes import Vec2D
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
		packetData = data[packetIDs.packetIDSize:]

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

class C2SMovementUpdate(Packet):
	def __init__(self, movDir: Vec2D) -> None:
		super().__init__(packetIDs.C2S_MOVEMENT_UPDATE)

		self.movDir = movDir
	
	@override
	def encodeData(self) -> bytes:
		# 2 bits for each delta. b'0000xxyy'
		bdx: int = 0
		match self.movDir.x:
			case 0:
				bdx = 0b00
			case 1:
				bdx = 0b01
			case -1:
				bdx = 0b10
			case _:
				print(f"error encoding movement bytes. unknown movement Direction x-value {self.movDir.x}")

		bdy: int = 0
		match self.movDir.y:
			case 0:
				bdy = 0b00
			case 1:
				bdy = 0b01
			case -1:
				bdy = 0b10
			case _:
				print(f"error encoding movement bytes. unknown movement Direction y-value {self.movDir.y}")
		
		encoded = (bdx << 2) + bdy
		return encoded.to_bytes(1)

	@override
	@staticmethod
	def decodeData(data: bytes) -> 'C2SMovementUpdate':
		packetData = data[packetIDs.packetIDSize:]

		packedDeltas = int.from_bytes(packetData)
		packedDy = packedDeltas >> 2
		packedDx = packedDeltas & 0b0011

		dx = 0
		match packedDx:
			case 0b00:
				dx = 0
			case 0b01:
				dx = 1
			case 0b10:
				dx = -1
			case _:
				print(f"error decoding movement bytes. unknown movement Direction x-value {packedDx}")

		dy = 0
		match packedDy:
			case 0b00:
				dy = 0
			case 0b01:
				dy = 1
			case 0b10:
				dy = -1
			case _:
				print(f"error decoding movement bytes. unknown movement Direction y-value {packedDy}")
		
		return C2SMovementUpdate(Vec2D(dx,dy))
