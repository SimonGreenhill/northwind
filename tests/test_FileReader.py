#!/usr/bin/env python
#coding=utf-8
"""Tests for Parsers/File"""
import sys
import unicodedata
import unittest
import warnings

sys.path.append('../bin')

from tools import FileReader, FileReaderException, Token, MissingToken


class Test_FileReader(unittest.TestCase):
    
    data_filename = 'test_data.txt'
    consonants = [
        "p(p, b)", "t(t, d)", "ʈ(ʈ, ɖ)", "c(c, ɟ)", 
        "k(k, g)", "m", "n", "ɳ", "ɲ", "ŋ", "l", 
        "ɭ", "ʎ", "r(r, ɾ, ɹ)", "ɻ", "j", "w"
    ]
    vowels = [
        "i(i, ɪ)", "iː(iː, ɛː)", "a(a, ɑ, ə, æ)",
        "aː(aː, ɑː)", "o(o, ɒ)", "u(u, ʊ)", "uː"
    ]
    consonants = [Token(t) for t in consonants]
    vowels = [Token(t) for t in vowels]
    
    @classmethod
    def setUpClass(cls):
        cls.reader = FileReader(cls.data_filename)
     
    def test_parse_sections(self):
        sections = [
            'Reference', 'Language', 'ISO Code', 'Consonant Inventory',
            'Vowel Inventory', 'Transcript', 'Notes', 'Errors',
        ]
        for section in sections:
            assert self.reader._parse_section("# %s" % section) == section
            assert self.reader._parse_section("#%s" % section) == section
            assert self.reader._parse_section("# %s:" % section) == section
            assert self.reader._parse_section("# %s  :" % section) == section
        
    def test_parse_sections_special_cases_note_notes(self):
        """Test that Note/Notes sections are handled correctly"""
        assert self.reader._parse_section("# Notes") == "Notes"
        assert self.reader._parse_section("# Note") == "Notes"
    
    def test_parse_section_titlecases(self):
        assert self.reader._parse_section("# other symbols") == "Other Symbols"
        assert self.reader._parse_section("# other Symbols") == "Other Symbols"
        assert self.reader._parse_section("# Other symbols") == "Other Symbols"
    
    def test_read_language(self):
        assert self.reader.data['Language'][0] == 'Bardi'

    def test_read_reference(self):
        assert self.reader.data['Reference'][0] == '10.1017/S00251003120000217'
    
    def test_read_iso_code(self):
        assert self.reader.data['ISO Code'][0] == 'bcj'
        
    def test_read_consonant_inventory(self):
        assert self.reader.data['Consonant Inventory'][0] == \
            "p(p, b), t(t, d), ʈ(ʈ, ɖ), c(c, ɟ), k(k, g),"
        assert self.reader.data['Consonant Inventory'][1] == \
            "m, n, ɳ, ɲ, ŋ, l, ɭ, ʎ, r(r, ɾ, ɹ), ɻ, j, w"
        
    def test_read_vowel_inventory(self):
        assert self.reader.data['Vowel Inventory'][0] == \
            "i(i, ɪ), iː(iː, ɛː), a(a, ɑ, ə, æ), aː(aː, ɑː), o(o, ɒ), u(u, ʊ), uː"
    
    def test_read_transcript(self):
        transcript = [
            "bɑːwɑɂ ‖ midəbɑʊ ‖ ɑɣɑl iːlɑ ɑgɑl gɑrjɑɭ cirə cɑwɑl ‖",
            "midɑbɑːw jɪnɑ cɑwɑl ɑgɑl | iːlɑ ‖ ɑgɑl gɑrcɑɭ ‖",
            "ulɒn | cubolɟubol ɪrɪn ‖",
            "ɻoəlɪ ɪnɲɑ ‖ miːdəbɑwə agal iːlə | bɑɖə | bɑlɪŋɑn ‖",
            "ɪnəmɪjɪn | miːdəbɑwnɪm ɪnɑmɪjɪn bɑːgɪdi |",
            "nɛːd ɪnəmɪjɪn  | gɑɳɖɪ | bɑɖə | ruəl inɲə cubol",
            "inɟʊ ‖ bɪləboŋgonɂ ‖",
            "giɲiŋgɔn | ɪmbɑɲiɟɪn ‖ ɪmbɑɲi | cubolb ɪnco ‖",
            "balab ɻuil ɪnɲa baɖ ar ɪndan ‖",
            "bʊlŋʊr ɲʊn ɪnɟal bɪləboŋ | garcaɭ ɪnɪn gaɳdɪ | bɪlɪlon",
            "iɲɟarələ ɲæləb |laɖaŋɑn injaliç | garɟaɭ | iːl agal",
            "midəbaw ɪŋarcarələ baɖə ‖",
            "wir ɪŋarjarmɪn jubol ɪŋɪɾɪn ɲuno pɪləboŋgon ‖",
            "puɲɟə ɪralɂ kaɾəgʊn iːla | miːdəpawə agal karcaɭ ‖",
            "olal ɪŋargaɖi | bɑːw agal | iːla | buɣun garɟəɭnɪm",
            "arə oːlalənəɾ ‖",
            "daral ɪŋorbul | bəlab | aŋanaɖ | garɟaɭnim",
            "ɪnɟalɪɾ aŋanaŋar | dɔrɔlb ɪŋorobol ‖",
            "ɲɑləbʊ | gɑɳɖ ɪnɪn bɪlɪlɔn gɑrɟɑɭ ‖",
            "gɪɲɪŋɣɔn wɪr ɪɲɟɑrmɪn bilɪlɔ bɑɖɪ ɲʊn ɪnɪn",
            "bɔɖɔɣɔn | gɑɳɖɪ gɑrɟɑɭ inɟɑɹgɪɟɪr ‖",
        ]
        transcript = [self.reader.standardise(t) for t in transcript]
        for i, line in enumerate(transcript):
            assert self.reader.data['Transcript'][i] == line
        # ensure we don't miss the last line
        assert self.reader.data['Transcript'][-1] == transcript[-1]
        
    def test_read_notes(self):
        assert self.reader.data['Notes'][0] == \
            "The text is a telling of Mercer Meyer's 'The Frog Story'."
    
    def test_errors(self):
        assert self.reader.data['Errors'][0] == '/x/ something'
        
    def test_known_missings(self):
        assert len(self.reader.known_missings) == 1
       
    def test_consonant_inventory(self):
        assert self.reader.data['consonants'] is not None
        
    def test_consonant_inventory_length(self):
        assert len(self.reader.data['consonants']) == len(self.consonants)
    
    def test_consonant_inventory_members(self):
        for i, c in enumerate(self.consonants):
            assert self.reader.data['consonants']
   
    def test_vowel_inventory(self):
        assert self.reader.data['vowels'] is not None
        
    def test_vowel_inventory_length(self):
        assert len(self.reader.data['vowels']) == len(self.vowels)
    
    def test_vowel_inventory_members(self):
        for i, c in enumerate(self.vowels):
            assert self.reader.data['vowels']
    
    def test_other_symbols(self):
        assert len(self.reader.data['Other Symbols']) == 1
    
    def test_other_symbols_parsing(self):
        os = self.reader.parse_list(self.reader.data['Other Symbols'])
        assert os == [Token('ɂ')]
        
    def test_other_symbols_go_into_other_symbols(self):
        assert Token('ɂ') in self.reader.other_symbols

    def test_other_symbols_skipped_in_transcript(self):
        found = [t for t in self.reader.transcript if t == Token('ɂ')]
        assert len(found) == 3, 'Should be 3 glottal stops'

    def test_other_symbols_not_in_missing(self):
        assert MissingToken("ɂ") not in self.reader.errors

    def test_cmp_etc(self):
        f = FileReader()
        g = FileReader()
        f.filename = 'f'
        g.filename = 'g'
        assert sorted([g,f]) == [f,g]
        assert f != g
        

class Test_FileReader_parse_inventory(unittest.TestCase):
    """
    Tests for parse_inventory to make sure that things are chunked
    properly
    
    Note: all strings going through reader need to passed through .standardise() first
    
    """
    @classmethod
    def setUpClass(cls):
        cls.reader = FileReader()
        
    def test_simple(self):
        s = self.reader.standardise('a')
        inv = self.reader.parse_inventory(s)
        assert repr(inv[0]) == "<a>"

    def test_three(self):
        s = self.reader.standardise('a b c')
        inv = self.reader.parse_inventory(s)
        assert repr(inv[0]) == "<a>"
        assert repr(inv[1]) == "<b>"
        assert repr(inv[2]) == "<c>"
    
    def test_allophone(self):
        s = self.reader.standardise('i(i, ɪ)')
        inv = self.reader.parse_inventory(s)
        assert len(inv) == 1
        assert repr(inv[0]) == "<i(i, ɪ)>"
        
    def test_allophone_and_something(self):
        s = self.reader.standardise('a i(i, ɪ) b')
        inv = self.reader.parse_inventory(s)
        assert len(inv) == 3
        assert repr(inv[0]) == "<a>"
        assert repr(inv[1]) == "<i(i, ɪ)>"
        assert repr(inv[2]) == "<b>"

    def test_length_colon(self):
        s = self.reader.standardise('a:')
        inv = self.reader.parse_inventory(s)
        assert len(inv) == 1
        assert repr(inv[0]) == "<aː>"  # note converted to triangle-triangle
        
    def test_length_triangles(self):
        s = self.reader.standardise('aː')
        inv = self.reader.parse_inventory(s)
        assert len(inv) == 1
        assert repr(inv[0]) == "<aː>"

    def test_length_and_something(self):
        s = self.reader.standardise('a bː c')
        inv = self.reader.parse_inventory(s)
        assert len(inv) == 3
        assert repr(inv[0]) == "<a>"
        assert repr(inv[1]) == "<bː>"
        assert repr(inv[2]) == "<c>"
    
    def test_complicated_1(self):
        data = "p, b, t̪, d, tʃ, dʒ, k(k, ʔ), g, m, n, ɲ, ŋ, s, h, w, j, l"
        expected = [
            "p", "b", "t̪", "d", "tʃ", "dʒ", "k(k, ʔ)", "g",
            "m", "n", "ɲ", "ŋ", "s", "h", "w", "j", "l"
        ]
        expected = [self.reader.standardise(e) for e in expected]
        inv = self.reader.parse_inventory(data)
        for i, value in enumerate(expected):
            assert repr(inv[i]) == "<%s>" % value, \
                'Expected %r, got %r' % (value, inv[i])
    
    def test_remove_missing_circle(self):
        inv = self.reader.parse_inventory(self.reader.standardise("◌̀"))
        assert repr(inv[0]) == "<%s>" % (unicodedata.lookup("COMBINING GRAVE ACCENT"))
    
    def test_error_on_mismatched_braces(self):
        with self.assertRaises(ValueError):
            self.reader.parse_inventory("a(a, b")
        with self.assertRaises(ValueError):
            self.reader.parse_inventory("a(a, b))")
        

class Test_FileReader_parse_list(unittest.TestCase):
    """
    Tests for parse_list to make sure that things are chunked
    properly
    """
    @classmethod
    def setUpClass(cls):
        cls.reader = FileReader()
    
    def test_no_error_section(self):
        assert self.reader.parse_list(None) == []
        assert self.reader.parse_list([]) == []
        
    def test_no_errors(self):
        assert self.reader.parse_list("") == []
    
    def test_simple_error(self):
        errors = self.reader.parse_list(["/x/ something"])
        assert errors == [MissingToken("x", known_missing=True)]
        assert errors[0].is_missing == True
        assert errors[0].known_missing == True
    
    def test_not_greedy(self):
        errors = self.reader.parse_list(["/x/ something/or other"])
        assert errors == [MissingToken("x", known_missing=True)]
        assert errors[0].is_missing == True
        assert errors[0].known_missing == True
    
    def test_combining_characters(self):
        errors = self.reader.parse_list(['/ ́/ tone'])
        assert len(errors) == 1
        assert errors[0].names == ['COMBINING ACUTE ACCENT']
        assert errors[0].is_missing == True
        assert errors[0].known_missing == True
        
    def test_2_chars(self):
        errors = self.reader.parse_list(['/||/'])
        assert len(errors) == 1
        assert errors[0].is_missing == True
        assert errors[0].known_missing == True
        assert len(errors[0].raw) == 2
    
    def test_long(self):
        errors = self.reader.parse_list(['/[...]/'])
        assert len(errors) == 1
        assert errors[0].is_missing == True
        assert errors[0].known_missing == True
        assert len(errors[0].raw) == 5

  
class Test_FileReader_parse_transcript(unittest.TestCase):
    """Test that FileReader parses the transcript section correctly"""
    @classmethod
    def setUpClass(cls):
        cls.reader = FileReader('test_data.txt')
        # remove most of the transcript for ease of testing
        cls.reader.data['Transcript'] = cls.reader.data['Transcript'][0:1]
    
    def test_get_variants(self):
        # allophone r(r, ɾ, ɹ)
        T = Token('r(r, ɾ, ɹ)')
        assert self.reader.get_variants()['r'] == T
        assert self.reader.get_variants()['ɾ'] == T
        assert self.reader.get_variants()['ɹ'] == T
        
    def test_get_exact(self):
        assert self.reader.get_exact('|') == ['|']
        assert self.reader.get_exact('‖') == ['‖']
        # length
        assert self.reader.get_exact('u') == ['u']
        assert self.reader.get_exact('uː') == ['uː']
        # allophone r(r, ɾ, ɹ)
        assert self.reader.get_exact('r') == ['r']
        assert self.reader.get_exact('ɾ') == ['ɾ']
        assert self.reader.get_exact('ɹ') == ['ɹ']

    def test_get_possible(self):
        assert sorted(self.reader.get_possible('u')) == sorted(['u', 'uː'])
        assert sorted(self.reader.get_possible('uː')) == sorted(['uː'])
     
    def test_get_missing(self):
        # if missing char is in the known_missings, then it returns a MissingToken
        # with known_missing set to True
        x = self.reader.get_missing('x')
        assert x == MissingToken('x')
        assert x.known_missing == True
        
        # if missing char is in the default_tokens, then it returns a Token
        # with phoneme_type="default"
        dot = self.reader.get_missing(".")
        assert dot == Token('.')
        assert dot.is_missing == False
        assert dot.phoneme_type == 'default'
        
        # otherwise it's just Missing
        nine = self.reader.get_missing('9')
        assert nine == MissingToken('9')
        assert nine.known_missing == False
    
    def test_is_boundary(self):
        for t in self.reader.transcript:
            if t in self.reader.boundary_tokens:
                assert self.reader.is_boundary(t), t
            else:
                assert not self.reader.is_boundary(t), t
    
    def test_is_combining(self):
        for char in self.reader.combining_tokens:
            assert self.reader.is_combining(char)
    
    def test_get_maximal(self):
        max_, store = self.reader.get_maximal(['i', 'ː'])
        assert max_ == ['i', 'ː']
        assert store == []
        
        max_, store = self.reader.get_maximal(['i', 'ː', 'x'])
        assert max_ == ['i', 'ː']
        assert store == ['x']
        
    def test_simple(self):
        parsed = self.reader.parse_transcript("ba")
        assert parsed[0] == Token("p(p, b)")
        assert parsed[1] == Token("a(a, ɑ, ə, æ)")
       
    def test_length(self):
        parsed = self.reader.parse_transcript("baːwɑ")
        assert parsed[0] == Token("p(p, b)")
        assert parsed[1] == Token("aː(aː, ɑː)")  # and NOT the same as a(a, ɑ, ə, æ)
        assert parsed[2] == Token("w")
        assert parsed[3] == Token("a(a, ɑ, ə, æ)")
    
    def test_length_with_no_subcomponent(self):
        # ɛ + ː -- there is no ɛ in the inventory.
        parsed = self.reader.parse_transcript("nɛːd")
        assert parsed[0] == Token("n")
        assert parsed[1] == Token("iː(iː, ɛː)")
        assert parsed[2] == Token("t(t, d)")
        
    def test_allophone(self):
        parsed = self.reader.parse_transcript("uwʊl")
        assert parsed[0] == Token("u(u, ʊ)")
        assert parsed[1] == Token("w")
        assert parsed[2] == Token("u(u, ʊ)")
        assert parsed[3] == Token("l")
        assert parsed[0] == parsed[2]
    
    def test_space(self):
        parsed = self.reader.parse_transcript("u ʊ")
        assert parsed[0] == Token("u(u, ʊ)")
        assert parsed[1] == Token(" ")
        assert parsed[2] == Token("u(u, ʊ)")
        
    def test_complex(self):
        parsed = self.reader.parse_transcript("midɑbɑːw jɪnɑ")
        assert parsed[0] == Token("m")               # m
        assert parsed[1] == Token("i(i, ɪ)")         # i
        assert parsed[2] == Token("t(t, d)")         # d
        assert parsed[3] == Token("a(a, ɑ, ə, æ)")   # a
        assert parsed[4] == Token("p(p, b)")         # b
        assert parsed[5] == Token("aː(aː, ɑː)")      # a:
        assert parsed[6] == Token("w")               # w
        assert parsed[7] == Token(" ")               # <space>
        assert parsed[8] == Token("j")               # j
        assert parsed[9] == Token("i(i, ɪ)")         # ɪ
        assert parsed[10] == Token("n")              # n
        assert parsed[11] == Token("a(a, ɑ, ə, æ)")  # a
    
    def test_nocrash_on_testdata(self):
        # read data again to get full complement...
        reader = FileReader('test_data.txt')
        for line in self.reader.data['Transcript']:
            # remove some stuff that I know aren't in the inventories.
            line = line.replace("ɣ", "").replace("ɔ", "").replace("ç", "")
            line = reader.standardise(line)
            self.reader.parse_transcript(line)
        
    def test_missing_token(self):
        string = "ɔlaɣ"
        parsed = self.reader.parse_transcript(string)
        assert len(parsed) == len(string)
        assert parsed[0] == MissingToken("ɔ")
        assert parsed[1] == Token("l")
        assert parsed[2] == Token("a(a, ɑ, ə, æ)")
        assert parsed[3] == MissingToken("ɣ")

    def test_duplication(self):
        string = "llall"
        parsed = self.reader.parse_transcript(string)
        assert len(parsed) == len(string)
        assert parsed[0] == Token("l")
        assert parsed[1] == Token("l")
        assert parsed[2] == Token("a(a, ɑ, ə, æ)")
        assert parsed[3] == Token("l")
        assert parsed[4] == Token("l")
        
    def test_slippage_and_duplication(self):
        string = "ɔlalɣ"
        parsed = self.reader.parse_transcript(string)
        assert len(parsed) == len(string)
        assert parsed[0] == MissingToken("ɔ")
        assert parsed[1] == Token("l")
        assert parsed[2] == Token("a(a, ɑ, ə, æ)")
        assert parsed[3] == Token("l")
        assert parsed[4] == MissingToken("ɣ")
        
    def test_unobserved(self):
        assert Token("ʎ") in self.reader.unobserved and Token("ʎ") not in self.reader.transcript
        assert Token("uː") in self.reader.unobserved and Token("uː") not in self.reader.transcript
        # NOTE: the following allophones are partially missing 
        #  1. ʈ(ʈ, ɖ)  -- no ʈ but some ɖ
        #  2. aː(aː, ɑː) -- no a: but some ɑː
    
    def test_transcript_property(self):
        assert self.reader.transcript == self.reader.data['tokenised_transcript']
    
    def test_identified_missing_characters(self):
        expected_missings = [
            Token("oː"), Token("ɣ"), Token("ɔ"), Token("ç"), MissingToken('ɂ')
        ]
        for m in self.reader.errors:
            assert m in expected_missings, '%s is not in expected_missings' % m

    

class Test_FileReader_BroadTranscript(unittest.TestCase):
    """Does test with a broad transcription"""
    data_filename = 'test_data_broadtranscript.txt'
    
    @classmethod
    def setUpClass(cls):
        cls.reader = FileReader(cls.data_filename)
        
    def test_choose_transcript_defaults_to_transcript(self):
        self.reader.data['Transcript'] = 'default'
        self.reader.data['Transcript - Broad'] = 'broad'
        self.reader.data['Transcript - Narrow'] = 'narrow'
        self.reader._choose_transcript()
        assert self.reader.data['Transcript'] == 'default'
        
    def test_choose_transcript_overrides_with_broad(self):
        self.reader.data['Transcript'] = None  # must be None
        self.reader.data['Transcript - Broad'] = 'broad'
        self.reader.data['Transcript - Narrow'] = 'narrow'
        self.reader._choose_transcript('broad')
        assert self.reader.data['Transcript'] == 'broad'
        
    def test_choose_transcript_overrides_with_narrow(self):
        self.reader.data['Transcript'] = None  # must be None
        self.reader.data['Transcript - Broad'] = 'broad'
        self.reader.data['Transcript - Narrow'] = 'narrow'
        self.reader._choose_transcript('narrow')
        assert self.reader.data['Transcript'] == 'narrow'
    
    def test_choose_transcript_error_on_invalid_type(self):
        with self.assertRaises(ValueError):
            self.reader.data['Transcript'] = None   # needed otherwise we default to Transcript
            self.reader._choose_transcript("sausage")
    

if __name__ == '__main__':
    unittest.main()
