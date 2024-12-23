import unittest

from common.c2sPackets import C2SMovementUpdate
from common.dataTypes import Vec2D


class packetTests(unittest.TestCase):
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
				decoded = p.decodeData(encoded)

				self.assertEqual(decoded.movDir, p.movDir)


