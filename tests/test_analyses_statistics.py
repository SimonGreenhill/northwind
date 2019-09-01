#!/usr/bin/env python
#coding=utf-8
import unittest
import sys

sys.path.append('../bin')
from tools import FileReader

sys.path.append('../analyses/statistics')
from get_statistics import describe

# just adding to coverage
import errors, overall

class Test_Summarise(unittest.TestCase):
    def setUp(self):
        glottolog = {'test_data': 'Nyulnyulan'}
        self.filereader = FileReader('test_data.txt')
        self.summary = describe(self.filereader, glottolog)
        
    def test_Language(self):
        assert self.summary['Language'] == 'test_data'  # no accents to remove
        
    def test_Label(self):
        assert self.summary['Label'] == 'test_data'  # no accents to remove
    
    def test_Family(self):
        assert self.summary['Family'] == 'Nyulnyulan'
    
    # Note that all the numerical values are cast to strings in describe()
    def test_InventoryLength(self):
        assert self.summary['InventoryLength'] == str(len(self.filereader.inventory))

    def test_Tokens(self):
        assert self.summary['Tokens'] == str(len(self.filereader.tokens))
    
    def test_TranscriptLength(self):
        assert self.summary['TranscriptLength'] == str(len(self.filereader.transcript))

    def test_Unobserved(self):
        assert self.summary['Unobserved'] == str(len(self.filereader.unobserved))

    def test_Errors(self):
        assert self.summary['Errors'] == str(len(self.filereader.errors))

    def test_DistinctErrors(self):
        assert self.summary['DistinctErrors'] == str(len(set(self.filereader.errors)))

    def test_AudioLength(self):
        assert self.summary['AudioLength'] == "NA"
