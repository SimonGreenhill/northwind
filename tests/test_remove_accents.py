#!/usr/bin/env python
#coding=utf-8
import unittest
import sys
sys.path.append('../bin')

from tools import remove_accents
    
class Test_RemoveAccents(unittest.TestCase):
    
    def test_no_change(self):
        assert remove_accents('simon') == 'simon'
    
    def test_remove(self):
        assert remove_accents("aáàǎâ") == 'aaaaa'
     
if __name__ == '__main__':
    unittest.main()
