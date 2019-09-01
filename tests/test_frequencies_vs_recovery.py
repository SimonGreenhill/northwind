#!/usr/bin/env python
#coding=utf-8
import unittest
import sys

sys.path.append('../bin')
from tools import Token
sys.path.append('../analyses/frequencies_vs_recovery')
from get_rates import read_phoible, to_phoible


class Test_ReadPhoible(unittest.TestCase):
    def test(self):
        ph = {t: i for (i, t) in read_phoible(END=200)}
        assert ph['s'] == 10
        assert ph['cç'] == 101
        assert ph['tsʼ'] == 111
        assert ph['ɻ'] == 200
        assert ph.get('nt') is None  # i.e. not 201
        # do we parse these correctly:
        # 94 n̠d̠ʒ = ndʒ
        assert ph['ndʒ'] == 94
        assert ph.get('n̠d̠ʒ') is None


class Test_to_phoible(unittest.TestCase):
    def setUp(self):
        self.phoible = {t: i for (i, t) in read_phoible()}
        
    def test_direct_match(self):
        self.assertEqual(to_phoible(Token("dʒ"), self.phoible), "dʒ")

    def test_root_token_match(self):
        self.assertEqual(to_phoible(Token("n(n, n̪, ɲ, ŋ)"), self.phoible), "n")
    
    def test_allophone_match(self):
        self.assertEqual(to_phoible(Token("X(X, əː)"), self.phoible), "əː")

    def test_fail(self):
        self.assertEqual(to_phoible(Token("X"), self.phoible), None)
    
    def test_g_colon(self):
        t = Token('gː')
        # in Central Sama, listed in inventory as g: (G + COLON). FileReader converts
        # colons to MODIFIER LETTER TRIANGULAR COLON
        self.assertEqual(to_phoible(t, self.phoible), 'gː')
        

if __name__ == '__main__':
    unittest.main()
