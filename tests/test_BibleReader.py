#!/usr/bin/env python
#coding=utf-8
import sys
sys.path.append('../bin')

import unittest
import warnings

from tools import BibleFileReader

class Test_BibleFileReader(unittest.TestCase):
    """Test Bible Additions"""
    @classmethod
    def setUpClass(cls):
        cls.reader = BibleFileReader('test_data_bible.txt')
    
    def test_read_bible(self):
        assert self.reader.data['Online Bible'][0] == 'Gospel of Mark'
        assert self.reader.data['Online Bible'][1] == 'http://paralleltext.info/data/arn-x-bible/41/001/'
    
    def test_read_bible_url(self):
        assert self.reader.bible_url == 'http://paralleltext.info/data/arn-x-bible/41/001/'


if __name__ == '__main__':
    unittest.main()
