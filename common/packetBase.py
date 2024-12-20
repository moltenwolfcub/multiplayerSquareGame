from abc import ABC, abstractmethod

class Packet(ABC):
	def __init__(self, id: int) -> None:
		self.id: int = id

	def getPacketId(self) -> int:
		return self.id
	
	def encode(self) -> bytes:
		encodedId = self.id.to_bytes(1)
		
		return encodedId + self.encodeData()

	@staticmethod
	def decodeID(data: bytes) -> int:
		return data[0]


	@abstractmethod
	@staticmethod
	def decodeData(data: bytes) -> 'Packet':
		pass

	@abstractmethod
	def encodeData(self) -> bytes:
		pass
