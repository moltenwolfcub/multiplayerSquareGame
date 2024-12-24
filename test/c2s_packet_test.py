import unittest

from common.c2s_packets import C2SHandshake, C2SMovementUpdate
from common.data_types import Vec2D


class c2sPackets(unittest.TestCase):
    """Tests for packets"""

    def testMovementPacket(self):
        packets = {
            C2SMovementUpdate(Vec2D( 0, 0)): " 0, 0",
            C2SMovementUpdate(Vec2D( 1, 0)): " 1, 0",
            C2SMovementUpdate(Vec2D(-1, 0)): "-1, 0",
            C2SMovementUpdate(Vec2D( 0, 1)): " 0, 1",
            C2SMovementUpdate(Vec2D( 0,-1)): " 0,-1",
        }

        for p in packets:
            with self.subTest(packet=packets[p]):
                encoded = p.encode()
                decoded = C2SMovementUpdate.decode_data(encoded)

                self.assertEqual(decoded.mov_dir, p.mov_dir)

    def testHandshakePacket(self):
        packet = C2SHandshake("test")

        encoded = packet.encode()
        decoded = C2SHandshake.decode_data(encoded)

        self.assertEqual(decoded.message, packet.message)
