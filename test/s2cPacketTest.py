import unittest

from common.dataTypes import Color, Vec2D
from common.player import CommonPlayer
from common.s2cPackets import S2CHandshake, S2CPlayers


class s2cPackets(unittest.TestCase):

	def testHandshakePacket(self):
		packet = S2CHandshake("test")

		encoded = packet.encode()
		decoded = S2CHandshake.decodeData(encoded)

		self.assertEqual(decoded.message, packet.message)

	def testPlayersPacket(self):
		packet = S2CPlayers([
			CommonPlayer(0, Vec2D(8,6), Vec2D(0,1), Color(128, 253,  43)),
			CommonPlayer(1, Vec2D(3,2), Vec2D(0,1), Color( 54, 127, 190)),
			CommonPlayer(2, Vec2D(4,7), Vec2D(0,1), Color(200, 235,  67)),
			CommonPlayer(3, Vec2D(9,9), Vec2D(0,1), Color(218,   0,   5))
		])

		encoded = packet.encode()
		decoded = S2CPlayers.decodeData(encoded)

		for i in range(len(packet.players)):
			expected = packet.players[i]
			actual = decoded.players[i]

			self.assertEqual(actual, expected)