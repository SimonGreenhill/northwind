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
        cls.reader = FileReader('test_data_bible.txt')
        
    def test_read_orthography_consonant_phoneme_correspondences(self):
        key = "Orthography Consonant Phoneme Correspondences"
        assert self.reader.data[key][0] == \
            "<p> = /p/, <t> = /t/-/t̪/, <k> = /k/, <ch> = /tʃ/, <tr> = /ʈʂ/,"
        assert self.reader.data[key][1] == \
            "<m> = /m/, <n> = /n/-/n̪/, <ñ> = /ɲ/, <ng> = /ŋ/, <f> = /f/, <d> = /θ/, <s> = /s/-/ʃ/,"
        assert self.reader.data[key][2] == \
            "<r> = /ʐ/, <g> = /ɣ/, <y> = /j/, <l> = /l/-/l̪/, <ll> = /ʎ/, <w> = /w/"
        
    def test_read_orthography_vowel_phoneme_correspondences(self):
        key = "Orthography Vowel Phoneme Correspondences"
        expected = unicodedata.normalize(
            "NFC", 
            "<i> = /ɪ/, <e> = /ë/, <a> = /ɐ̝/, <o> = /ö/, <u> = /ʊ/, <ü> = /ɘ/"
        )
        assert self.reader.data[key][0] == expected
        assert len(self.reader.data[key]) == 1
    
    def test_parse_orthography_single(self):
        # simple single character orthographies
        out = self.reader.parse_orthography("<p> = /p/, <k> = /k/", 'consonant')
        assert len(out) == 2
        assert out[0] == (Token("p"), [Token("p")])
        assert out[1] == (Token("k"), [Token("k")])
    
    def test_parse_orthography_multi(self):
        # multiple character orthographies
        out = self.reader.parse_orthography("<p> = /p/, <ch> = /tʃ/, <ng> = /ŋ/", 'consonant')
        assert len(out) == 3
        assert out[0] == (Token("p"), [Token("p")])
        assert out[1] == (Token("ch"), [Token("tʃ")])
        assert out[2] == (Token("ng"), [Token("ŋ")])
        
    def test_parse_orthography_overlapping(self):
        # orthographies with overlapping forms e.g.
        # <s> = /s/-/ʃ/
        # -> s in the orthgraphy could mean /s/ or /ʃ/ phoneme
        out = self.reader.parse_orthography("<p> = /p/, <s> = /s/-/ʃ/", 'consonant')
        assert len(out) == 2
        assert out[0] == (Token("p"), [Token("p")])
        assert out[1] == (Token("s"), [Token("s"), Token("ʃ")]), out[1]
        
    def test_read_orthography_vowel(self):
        out = self.reader.data['orthography_vowels']
        assert len(out) == 6
        assert out[0] == (Token("i"), [Token("ɪ")])
        assert out[1] == (Token("e"), [Token("ë")])
        assert out[2] == (Token("a"), [Token("ɐ̝")])
        assert out[3] == (Token("o"), [Token("ö")])
        assert out[4] == (Token("u"), [Token("ʊ")])
        assert out[5] == (Token("ü"), [Token("ɘ")])
        
    def test_read_orthography_consonant(self):
        out = self.reader.data['orthography_consonants']
        assert len(out) == 18, len(out)
        # "<p> = /p/, <t> = /t/-/t̪/, <k> = /k/, <ch> = /tʃ/, <tr> = /ʈʂ/,"
        assert out[0] == (Token("p"), [Token("p")]), "<p> = /p/"
        assert out[1] == (Token("t"), [Token("t"), Token("t̪")]), "<t> = /t/-/t̪/"
        assert out[2] == (Token("k"), [Token("k")]), "<k> = /k/"
        assert out[3] == (Token("ch"), [Token("tʃ")]), "<ch> = /tʃ/"
        assert out[4] == (Token("tr"), [Token("ʈʂ")]), "<tr> = /ʈʂ/"
        # "<m> = /m/, <n> = /n/-/n̪/, <ñ> = /ɲ/, <ng> = /ŋ/, <f> = /f/, <d> = /θ/, <s> = /s/-/ʃ/,"
        assert out[5] == (Token("m"), [Token("m")]), "<m> = /m/"
        assert out[6] == (Token("n"), [Token("n"), Token("n̪")]), "<n> = /n/-/n̪/"
        assert out[7] == (Token("ñ"), [Token("ɲ")]), "<ñ> = /ɲ/"
        assert out[8] == (Token("ng"), [Token("ŋ")]), "<ng> = /ŋ/"
        assert out[9] == (Token("f"), [Token("f")]), "<f> = /f/"
        assert out[10] == (Token("d"), [Token("θ")]), "<d> = /θ/"
        assert out[11] == (Token("s"), [Token("s"), Token("ʃ")]), "<s> = /s/-/ʃ/"
        # "<r> = /ʐ/, <g> = /ɣ/, <y> = /j/, <l> = /l/-/l̪/, <ll> = /ʎ/, <w> = /w/"
        assert out[12] == (Token("r"), [Token("ʐ")]), "<r> = /ʐ/"
        assert out[13] == (Token("g"), [Token("ɣ")]), "<g> = /ɣ/"
        assert out[14] == (Token("y"), [Token("j")]), "<y> = /j/"
        assert out[15] == (Token("l"), [Token("l"), Token("l̪")]), "<l> = /l/-/l̪/"
        assert out[16] == (Token("ll"), [Token("ʎ")]), "<ll> = /ʎ/"
        assert out[17] == (Token("w"), [Token("w")]), "<w> = /w/"
        
    def test_combined_orthography(self):
        assert len(self.reader.data['orthography']) == (6 + 18)


if __name__ == '__main__':
    unittest.main()
