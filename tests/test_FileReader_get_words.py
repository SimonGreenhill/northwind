#!/usr/bin/env python
#coding=utf-8
import sys
sys.path.append('../bin')

import unittest
import unicodedata
import warnings

from tools import FileReader, FileReaderException, Token


class Test_FileReaderOrthography(unittest.TestCase):
    """Test Orthography Functionality"""
    
    @classmethod
    def setUpClass(cls):
        cls.reader = FileReader('test_data.txt')
        # prune transcript to make testing easier 
        cls.reader.data['tokenised_transcript'] = cls.reader.transcript[0:76]
        cls.words = cls.reader.get_words()
    
    def test_get_words_count(self):
        assert len(self.words) == 12
    
    def test_get_words_one(self):
        assert self.words[0] == self.reader.parse_transcript("bɑːwɑ")
        
    def test_get_words_two(self):
        assert self.words[1] == self.reader.parse_transcript("midəbɑʊ")
        
    def test_get_words_with_missing(self):
        assert self.words[2] == self.reader.parse_transcript("ɑɣɑl")
    
    def test_get_words_last(self):
        assert self.words[11] == self.reader.parse_transcript("ɑgɑl")


if __name__ == '__main__':
    unittest.main()
