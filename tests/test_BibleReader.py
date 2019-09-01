#!/usr/bin/env python
#coding=utf-8
import sys
sys.path.append('../bin')

import unittest
import unicodedata
import warnings

from tools import BibleFileReader, Token, Ortheme


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
    
    def test_property(self):
        assert self.reader.orthography is not None
    
    def test_orthography(self):
        assert 'orthography' in self.reader.data
        assert len(self.reader.orthography) == 24
    
    def test_read_orthography_consonant_phoneme_correspondences(self):
        key = "Orthography Consonant Phoneme Correspondences"
        assert self.reader.data[key][0] == \
            "<p> = /p/, <t> = /t/-/t̪/, <k> = /k/, <ch> = /tʃ/, <tr> = /ʈʂ/,"
        assert self.reader.data[key][1] == \
            "<m> = /m/, <n> = /n/-/n̪/, <ñ> = /ɲ(ɲ. ɲː)/, <ng> = /ŋ/, <f> = /f/, <d> = /θ/, <s> = /s/-/ʃ/,"
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

    
    def test_read_orthography_vowel(self):
        ov = self.reader.data['orthography_vowels']
        assert len(ov) == 6
        assert ov[0] == Ortheme("<i> = /ɪ/", inventory=self.reader.inventory)
        assert ov[1] == Ortheme("<e> = /ë/", inventory=self.reader.inventory)
        assert ov[2] == Ortheme("<a> = /ɐ̝/", inventory=self.reader.inventory)
        assert ov[3] == Ortheme("<o> = /ö/", inventory=self.reader.inventory)
        assert ov[4] == Ortheme("<u> = /ʊ/", inventory=self.reader.inventory)
        assert ov[5] == Ortheme("<ü> = /ɘ/", inventory=self.reader.inventory)

    def test_read_orthography_consonant(self):
        oc = self.reader.data['orthography_consonants']
        assert len(oc) == 18, oc
        assert oc[0] == Ortheme("<p> = /p/", inventory=self.reader.inventory)
        assert oc[1] == Ortheme("<t> = /t/-/t̪/", inventory=self.reader.inventory)
        assert oc[2] == Ortheme("<k> = /k/", inventory=self.reader.inventory)
        assert oc[3] == Ortheme("<ch> = /tʃ/", inventory=self.reader.inventory)
        assert oc[4] == Ortheme("<tr> = /ʈʂ/", inventory=self.reader.inventory)
        assert oc[5] == Ortheme("<m> = /m/", inventory=self.reader.inventory)
        assert oc[6] == Ortheme("<n> = /n/-/n̪/", inventory=self.reader.inventory)
        assert oc[7] == Ortheme("<ñ> = /ɲ(ɲ, ɲː)/", inventory=self.reader.inventory)
        assert oc[8] == Ortheme("<ng> = /ŋ/", inventory=self.reader.inventory)
        assert oc[9] == Ortheme("<f> = /f/", inventory=self.reader.inventory)
        assert oc[10] == Ortheme("<d> = /θ/", inventory=self.reader.inventory)
        assert oc[11] == Ortheme("<s> = /s/-/ʃ/", inventory=self.reader.inventory)
        assert oc[12] == Ortheme("<r> = /ʐ/", inventory=self.reader.inventory)
        assert oc[13] == Ortheme("<g> = /ɣ/", inventory=self.reader.inventory)
        assert oc[14] == Ortheme("<y> = /j/", inventory=self.reader.inventory)
        assert oc[15] == Ortheme("<l> = /l/-/l̪/", inventory=self.reader.inventory)
        assert oc[16] == Ortheme("<ll> = /ʎ/", inventory=self.reader.inventory)
        assert oc[17] == Ortheme("<w> = /w/", inventory=self.reader.inventory)

    def test_combined_orthography(self):
        assert len(self.reader.orthography) == (6 + 18)

    def test_toIPA(self):
        text = self.reader.toIPA("ptkchtrmnñngfdsrgylwll")
        expected = [
            Token('p(p, pʰ, pʷ)'),
            Token('t'), # lost 't̪' as n:n
            Token('k(k, c, kʰ, cʰ, kʷ)'),
            Token('tʃ'),  # NOT <k(...)> and <h>
            Token('ʈʂ(ʈʂ, t̺s̺, t̺ʰ, ʈʰ)'),
            Token('m(m, mː)'),
            Token('n(n, nː, n̥ː)'),  # n, lost n̪ as n:n
            Token('ɲ(ɲ, ɲː)'),  # ñ
            Token('ŋ(ŋ, ɲ)'),   # ng
            Token('f(f, fʷ, fː)'),
            Token('θ'),
            Token('s'),  # lost ʃ as n:n
            Token('ʐ(ʐ, ɻ, ʂ, ɭ)'),
            Token('ɣ(ɣ, ʝ)'),
            Token('j(j, ʝ)'),
            Token('l(l, l̥, lː)'),  # lost l̪ as n:n
            Token('w'),
            Token('ʎ'),
        ]
        assert len(expected) == len(text)
        for i, e in enumerate(expected):
            assert e == text[i], 'Mismatch %d. %r : %r' % (i, repr(e), repr(text[i]))

    def test_toIPA_uses_lowercase(self):
        text = self.reader.toIPA("PTKCH")
        expected = [
            Token('p(p, pʰ, pʷ)'),
            Token('t'), # lost 't̪' as n:n
            Token('k(k, c, kʰ, cʰ, kʷ)'),
            Token('tʃ'),  # NOT <k(...)> and <h>
        ]
        assert len(expected) == len(text)
        
        for i, e in enumerate(expected):
            assert e == text[i], 'Mismatch %r : %r' % (e, text[i])

    def test_inventory_and_orthography_token_matches(self):
        # The orthographies tend to be underspecified e.g.:
        # p(p, pʰ, pʷ) is in the inventory but the orthography has
        # <p> = /p/
        # ... so we should first match the full and if not found then see
        # if we match the short form.
        assert 'p' in self.reader.get_variants()
        # ... and in orthography
        assert Ortheme('<p> = /p(p, pʰ, pʷ)/') in self.reader.orthography

        #...and in variants
        assert Token('p(p, pʰ, pʷ)') == self.reader.get_variants()['p']


if __name__ == '__main__':
    unittest.main()
