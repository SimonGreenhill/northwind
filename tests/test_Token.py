#!/usr/bin/env python
#coding=utf-8
"""Tests for Parsers/File"""
import unittest
import unicodedata
import sys
sys.path.append('../bin')

from tools import Token, MissingToken, TokenException


class Test_Token(unittest.TestCase):
    
    def test_compare(self):
        assert Token("p(p, b)") == Token("p(p, b)")
    
    def test_noncombining_forms_are_identical_to_combining(self):
        nfd = "".join([
            unicodedata.lookup("LATIN SMALL LETTER A"),
            unicodedata.lookup("COMBINING ACUTE ACCENT"),
        ])
        nfc = unicodedata.lookup("LATIN SMALL LETTER A WITH ACUTE")
        assert Token(nfc) == Token(nfd)
    
    def test_error_on_multiple_allophones(self):
        """Should raise error if multiple allophones"""
        with self.assertRaises(TokenException):
            Token("a (a, b) (c, d)")
    
    def test_is_missing(self):
        assert Token("X").is_missing == False
    
    def test_phoneme_type(self):
        assert Token("X").phoneme_type is None
        assert Token("!", phoneme_type="punctuation").phoneme_type == 'punctuation'
    
    def _fulltest(self, s, allophones, names):
        """Runs a full set of tests on the string `s`
        
        1. tests that the .raw value matches the original input `s`
        2. tests that the .token matches the original input `s`
        3. tests that the __repr__ is correct
        4. tests that the allophones are correctly extracted (list
            expected allophones in parameter `allophones`.
            Can be None)
        5. tests that the identified token names are correct (list
            expected names in parameter `names`)
        6. tests that variants list matches the expected
        """
        # standardise first as that's what Token does.
        s = unicodedata.normalize("NFC", s)
        if allophones:
            allophones = [unicodedata.normalize("NFC", a) for a in allophones]
        
        t = Token(s)
        try:
            # 1. tests that the .raw value matches the original input `s`
            assert t.raw == s, "Raw value %r != expected %r" % (t.raw, s)
            # 2. tests that the .token matches the original input `s`
            assert t.token == s.split("(")[0], \
                "Token %r != expected %r" % (t.token, s)
            # 3. tests that the __repr__ is correct
            assert repr(t) == '<%s>' % s, "Repr %r != expected <%r>" % (repr(t), s)
            # 4. tests that the allophones are correctly extracted
            assert t.allophones == allophones, \
                "Allophones %r != %r" % (t.allophones, allophones)
            # 5. tests that the identified token names are correct
            assert len(t.names) == len(names), \
                "Uneven amount of names: %r != %r" % (t.names, names)
            for i, name in enumerate(t.names):
                if name != names[i]:
                    raise AssertionError(
                        "Unexpected name %d, %s != %s" % (i, name, names[i])
                    )
            # 6. tests that variants list matches the expected
            if t.allophones is None:
                assert len(t.variants) == 1
                assert t.variants == [t.token]
            else:
                assert len(t.variants) == len(t.allophones)
                for a in t.allophones:
                    assert a in t.variants
        except AssertionError as e:  # pragma: no cover
            t.debug()
            raise e
        return True
    
    def test_p(self):
        self._fulltest("p", None, ["LATIN SMALL LETTER P"])
        
    def test_turned_y(self):
        self._fulltest("ʎ", None, ["LATIN SMALL LETTER TURNED Y"])
    
    def test_ai(self):
        self._fulltest(
            "ai",
            None,
            [
                "LATIN SMALL LETTER A",
                "LATIN SMALL LETTER I"
            ]
        )
    
    def test_a_length(self):
        self._fulltest(
            "aː",
            None,
            [
                "LATIN SMALL LETTER A",
                "MODIFIER LETTER TRIANGULAR COLON"
            ]
        )
    
    def test_b_allophone(self):
        self._fulltest(
            "b(b, b̥, β̞)",
            ["b", "b̥", "β̞"],
            [
                'LATIN SMALL LETTER B',
                'LATIN SMALL LETTER B',
                'LATIN SMALL LETTER B', 'COMBINING RING BELOW',
                'GREEK SMALL LETTER BETA', 'COMBINING DOWN TACK BELOW'
            ]
        )
    
    def test_d_allophone(self):
        self._fulltest(
            "d(d, ɾ, ð̞)",
            ["d", "ɾ", "ð̞"],
            [
                "LATIN SMALL LETTER D",
                'LATIN SMALL LETTER D',
                'LATIN SMALL LETTER R WITH FISHHOOK',
                'LATIN SMALL LETTER ETH', 'COMBINING DOWN TACK BELOW'
            ]
        )
    
    def test_a_allophone_large(self):
        self._fulltest(
            "a(a, á, à, aː, ḁ, a̰, ḁ̀)",
            ["a", "á", "à", "aː", "ḁ", "a̰", "ḁ̀"],
            [
                "LATIN SMALL LETTER A",
                'LATIN SMALL LETTER A',
                'LATIN SMALL LETTER A WITH ACUTE',
                'LATIN SMALL LETTER A WITH GRAVE',
                'LATIN SMALL LETTER A', 'MODIFIER LETTER TRIANGULAR COLON',
                'LATIN SMALL LETTER A WITH RING BELOW',
                'LATIN SMALL LETTER A', 'COMBINING TILDE BELOW',
                'LATIN SMALL LETTER A WITH RING BELOW', 'COMBINING GRAVE ACCENT',
            ]
        )
    
    def test_initial_char_in_allophones(self):
        # see test_regression.test_s_COMBINING_INVERTED_BRIDGE_BELOW_allophone
        # and test_regression.test_galician
        t = Token("b(b̥, β̞)")
        assert len(t.allophones) == 2
        assert "b̥" in t.allophones
        assert "β̞" in t.allophones
        assert len(t.variants) == 3
        assert "b" in t.variants
        assert "β̞" in t.variants
        assert "b̥" in t.variants
    
    def test_equals(self):
        assert Token("a") == Token("a")
        assert Token("a(a, á, à, aː, ḁ, a̰, ḁ̀)") == Token("a(a, á, à, aː, ḁ, a̰, ḁ̀)")
    
    def test_not_equals(self):
        assert Token("a") != Token("b")
        assert Token("a(a, á, à, aː, ḁ, a̰, ḁ̀)") != Token("a(a, á, à, aː, ḁ, ḁ̀)")
        assert Token("a(a, á, à, aː, ḁ, a̰, ḁ̀)") != Token("a")
    

class Test_MissingToken(unittest.TestCase):
    def test_missing_token(self):
        MissingToken()
    
    def test_is_missing(self):
        assert MissingToken("X").is_missing
    
    def test_phoneme_type(self):
        assert MissingToken("X").phoneme_type == 'missing'
    
    def test_repr(self):
        assert repr(MissingToken("X")) == "<MissingToken: X>"
    
    def test_repr_known_missing(self):
        assert repr(MissingToken("X", known_missing=True)) == "<KnownMissingToken: X>"
        
    
    def test_known_missing(self):
        assert MissingToken("X", known_missing=True).known_missing
        assert not MissingToken("X", known_missing=False).known_missing
        


if __name__ == '__main__':
    unittest.main()
