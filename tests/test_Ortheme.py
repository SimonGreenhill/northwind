#!/usr/bin/env python
#coding=utf-8
"""Tests for Parsers/File"""
import unittest
import unicodedata
import sys
sys.path.append('../bin')

from tools import Ortheme, OrthemeException, Token


class Test_Ortheme(unittest.TestCase):
    
    def test_1a(self):
        o = Ortheme("<p> = /p/")
        assert o.graphemes == [Token('p')]
        assert o.phonemes == [Token('p')]

    def test_2(self):
        o = Ortheme("<p>=/p/")
        assert o.graphemes == [Token('p')]
        assert o.phonemes == [Token('p')]

    def test_3(self):
        o = Ortheme("<ch> = /tʃ/")
        assert o.graphemes == [Token('ch')]
        assert o.phonemes == [Token('tʃ')]

    def test_4(self):
        o = Ortheme("<ieu>=/iu/")
        assert o.graphemes == [Token('ieu')]
        assert o.phonemes == [Token('iu')]

    def test_5(self):
        o = Ortheme("<ph>=/pʰ/")
        assert o.graphemes == [Token('ph')]
        assert o.phonemes == [Token('pʰ')]

    def test_6(self):
        o = Ortheme("<t> = /t/-/t̪/")
        assert o.graphemes == [Token('t')]
        assert o.phonemes == [Token('t'), Token('t̪')]

    def test_7(self):
        o = Ortheme("<n> = /n/-/ŋ/")
        assert o.graphemes == [Token('n')]
        assert o.phonemes == [Token('n'), Token('ŋ')]

    def test_8(self):
        o = Ortheme("<j>-<dd>=/ɟ/")
        assert o.graphemes == [Token('j'), Token('dd')]
        assert o.phonemes == [Token('ɟ')]

    def test_9(self):
        o = Ortheme("<l> = /ɮ/-/l/-/ɫ/")
        assert o.graphemes == [Token('l')]
        assert o.phonemes == [Token('ɮ'), Token('l'), Token('ɫ')]

    def test_10(self):
        o = Ortheme("<oe>-<œ>=/u/")
        assert o.graphemes == [Token('oe'), Token('œ')]
        assert o.phonemes == [Token('u')]

    def test_11(self):
        o = Ortheme("<k>-<q>-<c> = /k/")
        assert o.graphemes == [Token('k'), Token('q'), Token('c')]
        assert o.phonemes == [Token('k')]

    def test_12(self):
        o = Ortheme("<k>-<q>-<c> = /k/")
        assert o.graphemes == [Token('k'), Token('q'), Token('c')]
        assert o.phonemes == [Token('k')]

    def test_13(self):
        o = Ortheme("<s>-<c>-<ç>-<ss> = /s/")
        assert o.graphemes == [Token('s'), Token('c'), Token('ç'), Token("ss")]
        assert o.phonemes == [Token('s')]
    
    def test_14(self):
        o = Ortheme("<a(a, á, à, ả, ã, ạ)>=/a/")
        assert o.graphemes == [Token("a(a, á, à, ả, ã, ạ)")]
        assert o.phonemes == [Token('a')]

    def test_15(self):
        o = Ortheme("<i(i, í, ì, ị, ỉ, ĩ)>-<y(y, ý, ỳ, ỷ, ỹ, ỵ)>=/i/")
        assert o.graphemes == [Token("i(i, í, ì, ị, ỉ, ĩ)"), Token("y(y, ý, ỳ, ỷ, ỹ, ỵ)")]
        assert o.phonemes == [Token('i')]
    
    def test_repr(self):
        for o in ["<p> = /p/", "<n> = /n/-/ŋ/", "<k>-<q>-<c> = /k/"]:
            assert repr(Ortheme(o)) == o, "%s != %r" % (o, Ortheme(o))

    def test_compare(self):
        assert Ortheme("<p> = /p/") == Ortheme("<p>=/p/")
        assert Ortheme("<t> = /t/-/t̪/") == Ortheme("<t>=/t/-/t̪/")
        assert Ortheme("<t> = /t/-/t̪/") != Ortheme("<t>=/t/")
    
    def test_error_on_dash_separator(self):
        with self.assertRaises(OrthemeException):
            Ortheme("<eu>-/øə/")

    def test_error_on_multiple_separators(self):
        with self.assertRaises(OrthemeException):
            Ortheme("<eu>=/øə/=<aa>")
    
    def test_match_inventory_token(self):
        inv = [Token("i(i, í, ì, ị, ỉ, ĩ)"), ]
        o = Ortheme("<x>=/i/", inventory=inv)
        assert o.graphemes == [Token('x')]
        assert o.phonemes == inv

    def test_match_inventory_allophone(self):
        inv = [Token("i(i, í, ì, ị, ỉ, ĩ)"), ]
        o = Ortheme("<x>=/í/", inventory=inv)
        assert o.graphemes == [Token('x')]
        assert o.phonemes == inv

    def test_match_inventory_error(self):
        with self.assertRaises(ValueError):
            Ortheme("<x>=/a/", inventory=[Token("i(i, í, ì, ị, ỉ, ĩ)")])


if __name__ == '__main__':
    unittest.main()
