from abm_grant_interaction.bkt.bkt import Bkt

import unittest


class TestBkt(unittest.TestCase):

    def test_update(self):

        pL0_ = 0.0
        pT_ = 0.02
        pS_ = 0.3
        pG_ = 0.5

        bkt = Bkt(pL0_, pT_, pS_, pG_)
        pL_old = pL0_
        for _ in range(100):
            bkt.update(True)
            pL_new = bkt.get_automaticity()
            self.assertLess(pL0_, pL_new)
            self.assertLessEqual(pL_old, pL_new)
            self.assertNotEqual(1.0, pL_new)
            pL_old = pL_new

        for _ in range(100):
            bkt.update(False)
            pL_new = bkt.get_automaticity()
            self.assertGreaterEqual(pL_old, pL_new)
            self.assertNotEqual(1.0, pL_new)
            pL_old = pL_new

        self.assertAlmostEqual(0, pL_old)

    def test_update_assignment(self):

        pL0_ = 0.0
        pT_ = 0.02
        pS_ = 0.3
        pG_ = 0.5

        bkt = Bkt(pL0_, pT_, pS_, pG_)
        pL_old = pL0_
        for _ in range(100):
            bkt = bkt.update(True)
            pL_new = bkt.get_automaticity()
            self.assertLess(pL0_, pL_new)
            self.assertLessEqual(pL_old, pL_new)
            self.assertNotEqual(1.0, pL_new)
            pL_old = pL_new

        for _ in range(100):
            bkt = bkt.update(False)
            pL_new = bkt.get_automaticity()
            self.assertGreaterEqual(pL_old, pL_new)
            self.assertNotEqual(1.0, pL_new)
            pL_old = pL_new

        self.assertAlmostEqual(0, pL_old)

    def test_update_model(self):

        pL0_ = 0.0
        pT_ = 0.02
        pS_ = 0.3
        pG_ = 0.5

        bkt = Bkt(pL0_, pT_, pS_, pG_)
        bkt_true = bkt.fit([True]*100)
        bkt_false = bkt.fit([False]*100)
        bkt_mix = bkt.fit([True, False]*50)
        self.assertEqual(bkt, bkt)
        self.assertNotEqual(bkt, bkt_true)
        self.assertNotEqual(bkt, bkt_false)
        self.assertNotEqual(bkt_true, bkt_false)
        self.assertNotEqual(bkt, bkt_mix)
