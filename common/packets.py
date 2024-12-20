from abc import ABC, abstractmethod

class Packet(ABC):
	def __init__(self, name: str) -> None:
		self.name: str = name

	def getPacketName(self) -> str:
		return self.name

	@abstractmethod
	def encode(self) -> bytes:
		pass

	@abstractmethod
	@staticmethod
	def decode(data: bytes) -> 'Packet':
		pass
