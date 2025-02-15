import unittest

from common.bullet import CommonBullet
from common.data_types import Color, Vec2D
from common.player import CommonPlayer
from common.s2c_packets import S2CBullets, S2CDisconnectPlayer, S2CHandshake, S2CPlayers, S2CSendID


class s2cPackets(unittest.TestCase):

    def testHandshakePacket(self):
        packet = S2CHandshake("test")

        encoded = packet.encode()
        decoded = S2CHandshake.decode_data(encoded)

        self.assertEqual(decoded.message, packet.message)

    def testPlayersPacket(self):
        packet = S2CPlayers([
            CommonPlayer(0, Vec2D(8,6), Vec2D(0,1), Color(128, 253,  43)),
            CommonPlayer(1, Vec2D(3,2), Vec2D(0,1), Color( 54, 127, 190)),
            CommonPlayer(2, Vec2D(4,7), Vec2D(0,1), Color(200, 235,  67)),
            CommonPlayer(3, Vec2D(9,9), Vec2D(0,1), Color(218,   0,   5)),
        ])

        encoded = packet.encode()
        decoded = S2CPlayers.decode_data(encoded)

        for i, expected in enumerate(packet.players):
            actual = decoded.players[i]

            self.assertEqual(actual, expected)

    def testBulletsPacket(self):
        packet = S2CBullets([
            CommonBullet(Vec2D(128,  16), -1),
            CommonBullet(Vec2D(  0, 250), -1),
            CommonBullet(Vec2D(830, 678), -1),
        ])

        encoded = packet.encode()
        decoded = S2CBullets.decode_data(encoded)

        for i, expected in enumerate(packet.bullets):
            actual = decoded.bullets[i]

            self.assertEqual(actual, expected)

    def testSendID(self):
        packet = S2CSendID(5)

        encoded = packet.encode()
        decoded = S2CSendID.decode_data(encoded)

        self.assertEqual(packet.player_id, decoded.player_id)
    
    def testDisconnectPlayer(self):
        packet = S2CDisconnectPlayer(0)

        encoded = packet.encode()
        decoded = S2CDisconnectPlayer.decode_data(encoded)

        self.assertEqual(packet.reason, decoded.reason)
