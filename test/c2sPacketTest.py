import unittest

from common.c2sPackets import C2SHandshake, C2SMovementUpdate
from common.dataTypes import Vec2D


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
				decoded = C2SMovementUpdate.decodeData(encoded)

				self.assertEqual(decoded.movDir, p.movDir)

	def testHandshakePacket(self):
		packet = C2SHandshake("test")

		encoded = packet.encode()
		decoded = C2SHandshake.decodeData(encoded)

		self.assertEqual(decoded.message, packet.message)