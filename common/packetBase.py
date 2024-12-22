from abc import ABC, abstractmethod

from common import packetIDs


class Packet(ABC):
	def __init__(self, id: int) -> None:
		self.id: int = id

	def getPacketId(self) -> int:
		return self.id
	
	def encode(self) -> bytes:
		encodedId = self.id.to_bytes(packetIDs.packetIDSize)
		
		return encodedId + self.encodeData()

	@staticmethod
	def decodeID(data: bytes) -> int:
		return int.from_bytes(data[:packetIDs.packetIDSize])


	@staticmethod
	@abstractmethod
	def decodeData(data: bytes) -> 'Packet':
		pass

	@abstractmethod
	def encodeData(self) -> bytes:
		pass
