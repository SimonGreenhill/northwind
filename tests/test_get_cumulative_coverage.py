#!/usr/bin/env python
#coding=utf-8
import unittest
import sys
sys.path.append('../bin')

from tools import FileReader, Token, get_cumulative_coverage

class Test_GetCumulativeCoverage(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.reader = FileReader('test_data.txt')
        cls.cov = get_cumulative_coverage(cls.reader)
    
    def test_result(self):
        """Test metadata stored in Result objects"""
        assert self.cov[0].language == 'test_data'
        assert self.cov[0].isocode == 'bcj'
        
    def test_total_inventory_correct(self):
        invsize = len(self.reader.inventory)
        for res in self.cov:
            assert res.total_inv == invsize, "Expected %d got %d" % (invsize, res.total_inv)
    
    def test_0pc(self):
        res = self.cov[0]
        assert res.ppercent == 0
        assert res.position == 0
        assert res.observed == 0
        assert res.opercent == 0
        assert res.transcript == []
    
    def test_5pc(self):
        res = [c for c in self.cov if c.ppercent == 5][0]
        assert res.ppercent == 5
        assert res.position == 42  #  843 / 20 =  42.15
        assert res.observed == 15
        assert res.opercent == (15 / res.total_inv) * 100
        assert res.transcript[-1] == Token('r(r, ɾ, ɹ)')
    
    def test_100pc(self):
        res = self.cov[-1]
        assert res.ppercent == 100
        assert res.transcript[-1] == Token("‖")
        assert res.transcript == self.reader.transcript, "Should be full transcript"
        assert res.position == len(self.reader.transcript)


if __name__ == '__main__':
    unittest.main()
