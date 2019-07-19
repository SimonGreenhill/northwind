#!/usr/bin/env python
#coding=utf-8
import unittest
import sys
sys.path.append('../bin')

from get_glottolog_dat import get_values
    
class Test_GetGlottoLogDat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.values = get_values('test_glottolog.json')
    
    def test_ID(self):
        assert self.values['ID'] == 'kera1255'
     
    def test_ISO(self):
        assert self.values['ISO'] == 'ker'

    def test_Latitude(self):
        assert self.values['Latitude'] == 9.88165

    def test_Longitude(self):
        assert self.values['Longitude'] == 15.1419

    def test_Family(self):
        assert self.values['Family'] == 'Afro-Asiatic'

    def test_Classification(self):
        assert self.values['Classification'] == "Afro-Asiatic, Chadic, East Chadic, East Chadic A, East Chadic A A.3"


if __name__ == '__main__':
    unittest.main()
