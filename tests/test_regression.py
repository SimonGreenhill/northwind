#!/usr/bin/env python
#coding=utf-8
import unittest
import sys
sys.path.append('../bin')

from tools import FileReader, Token, MissingToken

# to help debug:
# import logging, sys
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


    
class Test_Regressions(unittest.TestCase):
    
    def test_overmatching(self):
        # this was being parsed as:
        #  [<h>, <ao>, <MissingToken: ̯>, <a>]
        # .. should be:
        #  [<h>, <a>, <o ̯>, <a>]
        
        # think this is only a problem where the full inventory
        # when a word is encountered in the form of:
        # 123
        # and the tokens "1", "12" and "23" exist.
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "h", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "i, e(e, e̯), ɜ, a, ɔ, o(o, o̯), u, ao",
            'vowel'
        )
        
        transcript = 'hao̯a'
        transcript = f.standardise(transcript)
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("h")
        assert parsed[1] == Token("a")
        assert parsed[2] == Token("o(o, o̯)")
        assert parsed[3] == Token("a")
    
    def test_maximal_error(self):
        # should identify the missing token as "o:" not ":"
        transcript = 'oːlal'
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "l, ɭ, ʎ, r(r, ɾ, ɹ)", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "a(a, ɑ, ə, æ), o(o, ɒ), u(u, ʊ), uː",
            'vowel'
        )
        
        transcript = f.standardise(transcript)
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == MissingToken("oː")
        assert parsed[1] == Token("l")
        assert parsed[2] == Token("a(a, ɑ, ə, æ)")
        assert parsed[3] == Token("l")

    def test_danish_overextension(self):
        # being parsed as  ... MissingToken("də") not MissingToken("d"),
        # Token("ə")
        transcript = 'b̥lɛːsdə'
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "b̥(b̥, b̥ʰ), d̥(d̥, d̥s), s, l(l, l̩)", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "e(e, eː), ɛ(ɛ, ɛː), a, ɑ, ə", 'vowel'
        )
        transcript = f.standardise(transcript)
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == MissingToken("b̥(b̥, b̥ʰ)")
        assert parsed[1] == Token("l(l, l̩)")
        assert parsed[2] == Token("ɛ(ɛ, ɛː)")
        assert parsed[3] == Token("s")
        assert parsed[4] == MissingToken("d")
        assert parsed[5] == Token("ə")
    
    def test_space_ends_word(self):
        # "cit ʔa" being parsed as 
        # 440.    iˑ                      vowel
        # 441.    c                       consonant
        # 442.    i                       missing       +
        # 443.    t ʔ                     missing       *
        # 444.    a                       vowel
        
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "c, t(t, tⁿ)", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "iˑ, a", 'vowel'
        )
        # add known missings
        f.known_missings = [
            MissingToken("i", known_missing=True),
            MissingToken("ʔ", known_missing=True),
        ]
        transcript = f.standardise("iˑcit ʔa")
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("iˑ")
        assert parsed[1] == Token("c")
        assert parsed[2] == MissingToken("i", known_missing=True)
        assert parsed[3] == Token("t(t, tⁿ)")
        assert parsed[4] == Token(" ")
        assert parsed[5] == MissingToken("ʔ", known_missing=True)
        assert parsed[6] == Token("a")
        
    def test_basaa_ignored_superscript_n(self):
        # gáː ⁿbɛ̀βí being parsed as
        #
        # 9.     h                       consonant
        # 10.    a(a, á, à, ǎ, â)    vowel
        # 11.    ŋ(ŋ, ŋ́, ŋ̀)            consonant
        # 12.    g                       missing       *
        # 13.    aː(aː, áː, àː, ǎː, âː)    vowel
        # 14.     ⁿ                      missing       *
        # 15.    b                       missing       *
        # 16.    ɛ(ɛ, ɛ́, ɛ̀, ɛ̌, ɛ̂)    vowel
        # 17.    β                       consonant
        # 18.    i(i, í, ì, ǐ, î)    vowel
        #
        # i.e. 14 should be combined with 15 = ⁿb
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "gʷ, ⁿb, ⁿg, β", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            """
            a(a, á, à, ǎ, â), aː(aː, áː, àː, ǎː, âː),
            e(e, é, è, ě, ê), ɛ(ɛ, ɛ́, ɛ̀, ɛ̌, ɛ̂),
            i(i, í, ì, ǐ, î),
            """,
            'vowels'
        )
        transcript = f.standardise('gáː ⁿbɛ̀βí')
        parsed = f.parse_transcript(transcript)
        
        assert parsed[0] == MissingToken("g")  # known missing
        assert parsed[1] == Token("aː(aː, áː, àː, ǎː, âː)")
        assert parsed[2] == Token(" ")  # was incorrect -- should be SPACE.
        assert parsed[3] == Token("ⁿb")  # was incorrect
        assert parsed[4] == Token("ɛ(ɛ, ɛ́, ɛ̀, ɛ̌, ɛ̂)")
        assert parsed[5] == Token("β")
        assert parsed[6] == Token("i(i, í, ì, ǐ, î)")
        
    def test_basaa_combining_n_only_attached_to_preceeding(self):
        # pêⁿbà being parsed as:
        # 43.	p                   	consonant
        # 44.	e(e, é, è, ě, ê)    	vowel
        # 45.	hⁿ                  	missing   	*
        # 46.	b                   	missing   	*
        # 47.	a(a, á, à, ǎ, â)    	vowel
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "p, h, ⁿb", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "e(e, é, è, ě, ê), a(a, á, à, ǎ, â)", 'vowels'
        )
        transcript = f.standardise('pêhⁿbà')
        parsed = f.parse_transcript(transcript)
        
        assert parsed[0] == Token("p")
        assert parsed[1] == Token("e(e, é, è, ě, ê)")
        assert parsed[2] == Token("h")
        assert parsed[3] == Token("ⁿb")
        assert parsed[4] == Token("a(a, á, à, ǎ, â)")
    
    def test_s_COMBINING_INVERTED_BRIDGE_BELOW(self):
        f = FileReader()
        f.data['consonants'] = f.parse_inventory("s̺", 'consonant')
        parsed = f.parse_transcript(f.standardise('s̺'))
        assert len(parsed) == 1
        assert parsed[0] == Token('s̺')
    
    def test_s_COMBINING_INVERTED_BRIDGE_BELOW_allophone(self):
        # the reason this failed was that s̺ isn't in the allophones
        # so s̺ didn't match anything. This is fixed at the Token level
        # and checked in test_Token.test_initial_char_in_allophones
        f = FileReader()
        f.data['consonants'] = f.parse_inventory("s̺(s, s̬, s̺)", 'consonant')
        parsed = f.parse_transcript(f.standardise('s̺'))
        assert len(parsed) == 1
        assert parsed[0] == Token('s̺(s, s̬, s̺)')
    
    def test_galician(self):
        # s̺oβ̞ɾe being parsed as:
        # 44.    s̺                      missing       *
        # 45.    o(o, õ, oː)             vowel
        # 46.    b(b, β̞)                consonant
        # 47.    ɾ                       consonant
        # 48.    e(e, ẽ)                 vowel
        #
        # the reason this failed was that s̺ isn't in the allophones
        # so s̺ didn't match anything. This is fixed at the Token level
        # and checked in test_Token.test_initial_char_in_allophones
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "s̺(s, s̬), b(b, β̞), ɾ", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "o(o, õ, oː), e(e, ẽ)", 'vowels'
        )
        transcript = f.standardise(' s̺oβ̞ɾe')
        parsed = f.parse_transcript(transcript)
        
        assert parsed[0] == Token(" ")
        assert parsed[1] == Token("s̺(s, s̬)")
        assert parsed[2] == Token("o(o, õ, oː)")
        assert parsed[3] == Token("b(b, β̞)")
        assert parsed[4] == Token("ɾ")
        assert parsed[5] == Token("e(e, ẽ)")
    
    def test_sandawe(self):
        # ǁ’àká being parsed as:
        # 489.    ‖                                      punctuation
        # 490.    ’                                      missing       *
        # 491.    a(a, á, à, ǎ, â)                       vowel
        # 492.    k                                      consonant
        # 
        # ǁ’ is in the inventory but I think it's being overriden by the default ǁ in boundary tokens
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "k, ǁ’", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "a(a, á, à, ǎ, â)", 'vowels'
        )
        transcript = f.standardise('ǁ’àká')
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("ǁ’")
        assert parsed[1] == Token("a(a, á, à, ǎ, â)")
        assert parsed[2] == Token("k")
        assert parsed[3] == Token("a(a, á, à, ǎ, â)")
    
    def test_sandawe_2(self):
        # ǀ’ùsù being parsed as:
        # 67.    |                                      punctuation
        # 68.    ’                                      missing       *
        # 69.    u(u, ú, ù, ǔ, û)                       vowel
        # 70.    s                                      consonant
        # 71.    u(u, ú, ù, ǔ, û)                   	vowel
        # 
        # ǀ’ in inventory but I think it's being overriden by the default ǁ in boundary tokens
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "s, ǀ’, x", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "u(u, ú, ù, ǔ, û)", 'vowels'
        )
        transcript = f.standardise('ǀ’ùsù')
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("ǀ’")
        assert parsed[1] == Token("u(u, ú, ù, ǔ, û)")
        assert parsed[2] == Token("s")
        assert parsed[3] == Token("u(u, ú, ù, ǔ, û)")
    
    def test_rhotic_hook(self):
        # lia˞u˞
        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "l", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "i, au(au, a˞u˞)", 'vowels'
        )
        transcript = f.standardise('lia˞u˞')
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("l")
        assert parsed[1] == Token("i")
        assert parsed[2] == Token("au(au, a˞u˞)")
    
    def test_upper_xumi(self):
        # an error with large other symbols being identified as single ones.
        # e.g. here "||" is being identified as two "|" i.e. "|", "|"
        f = FileReader()
        f.data['consonants'] = f.parse_inventory("l H", 'consonant')
        f.data['vowels'] = f.parse_inventory("i", 'vowels')
        f.known_missings.update(f.parse_list(["/|/", "/||/"]))
        transcript = f.standardise("li || H")
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("l")
        assert parsed[1] == Token("i")
        assert parsed[2] == Token(" ")
        assert parsed[3] == Token("||")
        assert parsed[4] == Token(" ")
        assert parsed[5] == Token("H")
    
    def test_ellipsis(self):
        # an error with ellipsis. [...]
        f = FileReader()
        f.data['consonants'] = f.parse_inventory("l n", 'consonant')
        f.data['vowels'] = f.parse_inventory("", 'vowels')
        f.known_missings.update(f.parse_list(["/[...]/"]))
        transcript = f.standardise("l [...] n")
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("l")
        assert parsed[1] == Token(" ")
        assert parsed[2] == Token("[...]")
        assert parsed[3] == Token(" ")
        assert parsed[4] == Token("n")
    
    def test_shilluk(self):
        f = FileReader()
        f.data['consonants'] = f.parse_inventory("ŋ", 'consonant')
        f.data['vowels'] = f.parse_inventory(
            "ɪ(ɪ́, ɪ̄, ɪ̀, ɪ̌, ɪ̂, ɪ̂́), a(á, ā, à, ǎ, â), ɪː(ɪ́ː, ɪ̄ː, ɪ̀ː, ɪ̌ː, ɪ̂ː, ɪ̂́ː)",
            'vowels'
        )
        transcript = f.standardise("ɪ̂́ŋ-à")
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("ɪ(ɪ́, ɪ̄, ɪ̀, ɪ̌, ɪ̂, ɪ̂́)")
        assert parsed[1] == Token("ŋ")
        assert parsed[2] == Token("-")
        assert parsed[3] == Token("a(á, ā, à, ǎ, â)")

    def test_combining_in_others(self):
        # Setswana's 'bó̝kɔ̝̀ːnì' was being parsed as:
        #
        # 8.    b                                      consonant
        # 9.    o̝(o̝, ò̝, ó̝, ô̝, ǒ̝)                 vowel
        # 10.    k                                      consonant
        # 11.    ɔ̝̀ː                                   missing       *
        # 12.    n                                      consonant
        # 13.    i(i, ì, í, î, ǐ, ì̞, í̞)               vowel
        #
        # i.e. in token 11 the combining character of double triangle "ː" is 
        # merged to the character 'ɔ̝̀'. 'ɔ̝̀' is IN the inventory, but 'ɔ̝̀ː' is NOT
        # so this gets flagged as an error. "ː" is in other symbols and is
        # currently not being recognized as such


        f = FileReader()
        f.data['consonants'] = f.parse_inventory(
            "b, k, n", 'consonant'
        )
        f.data['vowels'] = f.parse_inventory(
            "o̝(o̝, ò̝, ó̝, ô̝, ǒ̝), i(i, ì, í, î, ǐ, ì̞, í̞)",
            'vowel'
        )
        f.known_missings.update(f.parse_list(['/ɔ̝̀/']))
        f.other_symbols.update(f.parse_inventory('ː', 'other'))
        # Other: ː
        transcript = 'bó̝kɔ̝̀ːnì'
        transcript = f.standardise(transcript)
        parsed = f.parse_transcript(transcript)
        assert parsed[0] == Token("b"), parsed
        assert parsed[1] == Token("o̝(o̝, ò̝, ó̝, ô̝, ǒ̝)"), parsed
        assert parsed[2] == Token("k"), parsed
        assert parsed[3] == MissingToken("ɔ̝̀"), parsed
        assert parsed[4] == Token("ː"), parsed
        assert parsed[5] == Token("n"), parsed
        assert parsed[6] == Token("i(i, ì, í, î, ǐ, ì̞, í̞)"), parsed


class Test_Mambai(unittest.TestCase):
    def setUp(self):
        self.f = FileReader()
        self.f.data['consonants'] = self.f.parse_inventory("""
        p, b, t, d, k, g(g, k̚, q̚, ɣ, ʁ), kp(kp, kpŋm), gb, ɓ(ɓ, ʔm̰, ʔɓ, ʔp),
        ɗ(ɗ, ʔn̰, ʔɗ, ʔl̰), m, n, ŋ, ⱱ̟, ɽ(ɽ, ɳ̆, r), f, v, s, z, h, j(j, ɲ), 
        ʔj̰(ʔj̰, ʔɲ̰), w(w, ŋʷ), ʔw̰(ʔw̰, ʔŋ̰ʷ, ʔẁ̰), l(l, n), ʔ
        """, "consonant")
        self.f.data['vowels'] = self.f.parse_inventory("""
        i(i, í, ì, î, ĭ̀, ĭ́, íʔḭ̆́),
        ĩ(ĩ, ĩ́, ĩ̀, ĩ̂),
        ḭ̃(ḭ̃, ḭ̃́, ḭ̃̀, ḭ̃̂),
        ḭ(ḭ, ḭ́, ḭ̀, ḭ̂, iʔḭ),
        iː(iː, íː, ìː, îː),
        ĩː(ĩː, ĩ́ː, ĩ̀ː, ĩ̂ː),
        iˤ(iˤ, íˤ, ìˤ, îˤ, eˤ, éˤ, èˤ, êˤ),
        ĩˤ(ĩˤ, ĩ́ˤ, ĩ̀ˤ, ĩ̂ˤ), ẽˤ(ẽˤ, ẽ́ˤ, ẽ̀ˤ, ẽ̂ˤ),
        
        e(e, é, è, ê),
        ḛ(ḛ, ḛ́, ḛ̀, ḛ̂, eʔḛ, èʔḛ̆),
        eː(e:, éː, èː, êː),
        ḛ̃(ḛ̃, ḛ̃́, ḛ̃̀, ḛ̃̂),

        a(a, á, à, â),
        ã(ã, ã́, ã̀, ã̂),
        a̰(a̰, á̰, ắ̰, à̰, â̰, aʔa̰, áʔằ̰, áʔắ̰),
        aː(aː, áː, àː, âː), 
        ãː(ãː, ã́ː, ã̀ː, ã̂ː),
        aˤ(aˤ, áˤ, àˤ, âˤ),
        ãˤ(ãˤ, ã́ˤ, ã̀ˤ, ã̂ˤ), õˤ(õˤ, ṍˤ, õ̀ˤ, õ̂ˤ),
        ã̰(ã̰, ã̰́, ã̰̀, ã̰̂),

        o(o, ó, ò, ô, ŏ̀),
        o̰(o̰, ó̰, ò̰, ô̰, oʔo̰, óʔŏ̰́),
        oː(oː, óː, òː, ôː),
        õ̰(õ̰, ṍ̰, õ̰̀, õ̰̂),

        u(u, ú, ù, û),
        ũ(ũ, ṹ, ũ̀, ũ̂), 
        ṵ(ṵ, ṵ́, ṵ̀, ṵ̂, uʔṵ, úʔṵ̆́, úʔṵ̆̀, ùʔṵ̆̀),
        uː(uː, úː, ùː, ûː),
        ũː(ũː, ṹː, ũ̀ː, ũ̂ː), 
        uˤ(uˤ, úˤ, ùˤ, ûˤ, oˤ, óˤ, òˤ, ôˤ), 
        ũˤ(ũˤ, ṹˤ, ũ̀ˤ, ũ̂ˤ), 
        ṵ̃(ṵ̃, ṵ̃́, ṵ̃̀, ṵ̃̂)
        """, "vowel")
        self.f.known_missings.update(self.f.parse_list(
            ["/↗/", ]
        ))
    
    def test_get_maximal(self):
        max_, store = self.f.get_maximal(['ó', 'ʔ', 'ẁ̰'])
        assert max_ == ['ó']
        assert store == ['ʔ', 'ẁ̰']
    
    def test_one(self):
        # parsed as 
        #130.	j(j, ɲ)                            	consonant
        #131.	o(o, ó, ò, ô, ŏ̀)                  	vowel
        #132.	↗                                  	other
        #133.	óʔẁ̰                               	missing   	*
        #134.	                                   	punctuation
        transcript = self.f.standardise("jó↗óʔẁ̰")
        parsed = self.f.parse_transcript(transcript)
        assert parsed[0] == Token("j(j, ɲ)")
        assert parsed[1] == Token("o(o, ó, ò, ô, ŏ̀)")
        assert parsed[2] == MissingToken("↗")
        assert parsed[3] == Token("o(o, ó, ò, ô, ŏ̀)")
        assert parsed[4] == Token("ʔw̰(ʔw̰, ʔŋ̰ʷ, ʔẁ̰)")
        
     
        
if __name__ == '__main__':
    unittest.main()
