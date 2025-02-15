from abc import ABC, abstractmethod

from common import packet_ids


class Packet(ABC):
    def __init__(self, id: int) -> None:
        self.id: int = id

    def get_packet_id(self) -> int:
        return self.id
    
    def encode(self) -> bytes:
        encoded_id = self.id.to_bytes(packet_ids.packet_id_size, byteorder="big")
        
        return encoded_id + self.encode_data()

    @staticmethod
    def decode_id(data: bytes) -> int:
        return int.from_bytes(data[:packet_ids.packet_id_size], byteorder="big")


    @staticmethod
    @abstractmethod
    def decode_data(data: bytes) -> 'Packet':
        pass

    @abstractmethod
    def encode_data(self) -> bytes:
        pass
