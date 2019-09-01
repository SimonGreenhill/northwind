#!/usr/bin/env python
#coding=utf-8
import unittest
import sys
sys.path.append('../bin')

from tools import get_audio
    
class Test_GetAudio(unittest.TestCase):
    
    def test_nothing(self):
        assert get_audio([]) == None
        assert get_audio(['', '']) == None
        assert get_audio(None) == None
    
    def test_NA(self):
        assert get_audio(["NA"]) == None
    
    def test_time(self):
        assert get_audio(["111"]) == 111

    def test_time_float(self):
        assert get_audio(["11.1"]) == 11.1
        
    def test_invalid(self):
        with self.assertRaises(ValueError):
            assert get_audio(['1.a'])
        
    
if __name__ == '__main__':
    unittest.main()
