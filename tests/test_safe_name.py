#!/usr/bin/env python
#coding=utf-8
import unittest
import sys
sys.path.append('../bin')

from tools import safe_name
    
class Test_SafeName(unittest.TestCase):
    
    def test_no_change(self):
        assert safe_name('simon') == 'simon'
    
    def test_braces(self):
        assert safe_name('simon(2)') == 'simon2'
        
    def test_space(self):
        assert safe_name("si mon") == 'si_mon'
        
    def test_dash(self):
        assert safe_name("si-mon") == 'simon'
    
    def test_removes_accents(self):
        assert safe_name("aáàǎâ") == 'aaaaa'
         
     
if __name__ == '__main__':
    unittest.main()
