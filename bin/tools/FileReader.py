#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding=utf-8

import os
import re
import codecs
import logging
import unicodedata

from .Token import Token, MissingToken

IGNORE_CHARACTER = unicodedata.lookup('DOTTED CIRCLE'),



class FileReaderException(Exception):
    pass


class FileReader(object):
    
    _is_record = re.compile(r"""/(.*?)/""")
    _is_orthography_grapheme = re.compile(r"""<(.*)>""")
    _is_orthography_phoneme = re.compile(r"""/(.*)/""")
    
    # maximum number of times to iterate in parse_transcript -- should help
    # handle catastrophic parsing failures.
    _max_iterate_length = 10000
    
    boundary_tokens = set([
        Token(" ", phoneme_type="punctuation"),
    ])
    
    default_tokens = set([
        # , - comma = either stress, or used by some authors to indicate
        # intonation breaks
        Token(",", phoneme_type="punctuation"),
        # . - full stop = used by some authors to indicate clause or intonation
        # boundaries
        Token(".", phoneme_type="punctuation"),
        # misc
        Token(";", phoneme_type="punctuation"),
        Token("(", phoneme_type="punctuation"),
        Token(")", phoneme_type="punctuation"),
        Token("/", phoneme_type="punctuation"),
        # stress
        Token('ˈ', phoneme_type="stress"),
        Token('ˌ', phoneme_type="stress"),
        Token('-', phoneme_type="misc"),  # e.g. clitic marker
        # | - vertical bar = prosodic boundary
        Token(unicodedata.lookup("VERTICAL LINE"), phoneme_type="punctuation"),
        # # ‖ - double vertical bar = prosodic boundary
        Token(unicodedata.lookup("DOUBLE VERTICAL LINE"), phoneme_type="punctuation"),
    ])
    
    combining_tokens = [
        unicodedata.lookup('MODIFIER LETTER TRIANGULAR COLON'),
        unicodedata.lookup('MODIFIER LETTER RHOTIC HOOK'),
        unicodedata.lookup('COMBINING ACUTE ACCENT'),
        unicodedata.lookup('COMBINING GRAVE ACCENT'),
        unicodedata.lookup('COMBINING CIRCUMFLEX ACCENT'),
        unicodedata.lookup('COMBINING CARON'),
        unicodedata.lookup('COMBINING TILDE'),
        unicodedata.lookup('COMBINING TILDE BELOW'),
        unicodedata.lookup('COMBINING BREVE'),
        unicodedata.lookup('COMBINING INVERTED BREVE BELOW'),
        unicodedata.lookup('COMBINING INVERTED BRIDGE BELOW'),
        unicodedata.lookup('COMBINING RING BELOW'),
        unicodedata.lookup('COMBINING RIGHT TACK BELOW'),
        unicodedata.lookup('COMBINING VERTICAL LINE BELOW'),
        unicodedata.lookup('COMBINING ACUTE ACCENT'),
        unicodedata.lookup('COMBINING UP TACK BELOW'),
        unicodedata.lookup('COMBINING X ABOVE'),
        unicodedata.lookup('RIGHT SINGLE QUOTATION MARK'),
        unicodedata.lookup('MODIFIER LETTER SMALL GAMMA'),
    ]
    combining_tokens = set([
        Token(t, phoneme_type="combiner") for t in combining_tokens
    ])
    
    
    def __init__(self, filename=None, preferred_transcript="broad"):
        self.filename = filename
        self.preferred_transcript = preferred_transcript
        self.logger = logging.getLogger('FileReader:%s' % self.filename)
        self.other_symbols = set()
        self.known_missings = set()
        self.data = {
            # Note: Titlecase values are raw from data file.
            'Reference': None,
            'Language': None,
            'ISO Code': None,
            'Consonant Inventory': None,
            'Vowel Inventory': None,
            'Toneme Inventory': None,
            'Transcript': None,
            'Transcript - Broad': None,
            'Transcript - Narrow': None,
            'Notes': None,
            'Online Bible': None,
            'Orthography Consonant Phoneme Correspondences': None,
            'Orthography Vowel Phoneme Correspondences': None,
            'Orthography Notes': None,
            'Other Symbols': None,
            'Minimal Pairs': None,
            'Minimal Pair Examples': None,
            'Errors': None,
            'NWS': None,
            # lowercase labels are processed/computed fields.
            'vowels': None,
            'consonants': None,
            'tones': None,
            'other_symbols': None,
            'tokenised_transcript': None,
            'orthography_vowels': None,
            'orthography_consonants': None,
            'orthography': None,
        }
        
        # sections to standardise the orthography of
        self._to_standardise = [
            'Consonant Inventory',
            'Vowel Inventory',
            'Transcript', 'Transcript - Broad', 'Transcript - Narrow',
            'Notes', 'Errors',
            'Orthography Consonant Phoneme Correspondences',
            'Orthography Vowel Phoneme Correspondences',
            'Orthography Notes',
            'Other Symbols',
        ]
        
        if self.filename:
            self.read(filename)
            self.language = os.path.splitext(
                os.path.basename(filename)
            )[0]
            
    def __repr__(self):
        return "FileReader: %s" % self.filename
    
    def __cmp__(self):
        return self.filename
        
    def __lt__(self, other):
        return self.filename < other.filename
    
    # this lambda makes some of the code below more legible
    join = lambda self, x: " ".join([_.strip() for _ in x]) if x else ''
    
    def _parse_section(self, section):
        """Simple section label parser"""
        if section[0] == '#':
            section = section[1:]
        section = section.strip().strip(":").strip()
        
        # title case
        if section != 'ISO Code':
            section = section.title()
        
        # special casing of note/s
        if section == 'Note':
            section = 'Notes'
        # error on unknown section
        if section not in self.data:
            self.data[section] = []
        return section
    
    def _choose_transcript(self, preferred_transcript='broad'):
        """
        Decides which transcript to store in self.data['Transcript']
        
        If `Transcript` section has been found, keep that (default)
        If preferred_transcript is 'broad' choose 'Transcript - Broad' section
        If preferred_transcript is 'narrow' choose 'Transcript - Narrow'
        section
        
        Raises ValueError if neither Transcript nor the preferred_transcript is
        set.
        """
        # default
        if self.data['Transcript'] is not None:
            return
        # broad
        if preferred_transcript == 'broad':
            if self.data['Transcript - Broad'] is None:  # pragma: no cover
                raise ValueError("Broad Transcript wanted but not found")
            self.data['Transcript'] = self.data['Transcript - Broad']
        # narrow
        elif preferred_transcript == 'narrow':
            if self.data['Transcript - Narrow'] is None:  # pragma: no cover
                raise ValueError("Narrow Transcript wanted but not found")
            self.data['Transcript'] = self.data['Transcript - Narrow']
        # unknown type
        else:
            raise ValueError(
                "Unknown Preferred Transcript Type: %s" % preferred_transcript
            )
        return
    
    def _process_standardisation(self):
        """Standardise blocks that need it"""
        for section in self._to_standardise:
            if self.data[section] is not None:
                self.logger.debug("standardising %s" % section)
                self.data[section] = [
                    self.standardise(l) for l in self.data[section]
                ]
        
    def _process_tokens(self):
        """tokenise sections that need it."""
        self.logger.debug("parse_inventory:consonants")
        self.data['consonants'] = self.parse_inventory(
            self.join(self.data['Consonant Inventory']), 'consonant'
        )
        self.logger.debug("parse_inventory:vowels")
        self.data['vowels'] = self.parse_inventory(
            self.join(self.data['Vowel Inventory']), 'vowel'
        )
        self.logger.debug("parse_inventory:tones")
        self.data['tones'] = self.parse_inventory(
            self.join(self.data['Toneme Inventory']), 'tone'
        )
        # tonemes get handed to other symbols as we can't handle them
        self.other_symbols.extend(self.data['tones'])
        
        self.logger.debug("parse_inventory:tokenised_transcript")
        self.data['tokenised_transcript'] = self.parse_transcript(
            self.join(self.data['Transcript'])
        )
        return
    
    def _process_orthography(self):
        """Process Orthography blocks"""
        OCPC = 'Orthography Consonant Phoneme Correspondences'
        OVPC = 'Orthography Vowel Phoneme Correspondences'
        if OVPC in self.data and OCPC in self.data:
            self.data['orthography'] = []

        # orthography
        if self.data[OCPC]:
            self.logger.debug("parse_inventory:orthography_consonants")
            self.data['orthography_consonants'] = self.parse_orthography(
                self.join(self.data[OCPC]), 'consonant'
            )
            self.data['orthography'].extend(
                self.data['orthography_consonants']
            )
        
        if self.data[OVPC]:
            self.logger.debug("parse_inventory:orthography_vowels")
            self.data['orthography_vowels'] = self.parse_orthography(
                 self.join(self.data[OVPC]), 'vowel'
            )
            self.data['orthography'].extend(
                self.data['orthography_vowels']
            )
        return
    
    @property
    def unobserved(self):
        """Returns a list of things missing from the transcript"""
        return [t for t in self.inventory if t not in self.transcript]

    @property
    def missing(self):
        raise DeprecationWarning("missing is now renamed to errors")
        
    @property
    def errors(self):
        """
        Returns a list of errors (i.e. things missing from the inventory but seen in
        tokens
        """
        if self.data['tokenised_transcript'] is None:
            return []
        else:
            return [t for t in self.data['tokenised_transcript'] if t.is_missing]
    
    # expose some data as properties as this makes subsequent code prettier
    @property
    def inventory(self):
        """
        The defined inventory in the paper (consonants, vowels)
        """
        inv = []
        if self.data.get('consonants', None) is not None:
            inv.extend(self.data['consonants'])
        if self.data.get('vowels', None) is not None:
            inv.extend(self.data['vowels'])
        # leave tones out as they're not consistent across languages.
        # if self.data.get('tones', None) is not None:
        #     inv.extend(self.data['tones'])
        return inv
    
    @property
    def tokens(self):
        """
        The actual full inventory (including known_missings and other_symbols)
        
        i.e. all the tokens defined in the file.
        """
        inv = self.inventory[:]
        if self.other_symbols:
            inv.extend(self.other_symbols)
        if self.known_missings:
            inv.extend(self.known_missings)
        return inv

    @property
    def transcript(self):
        return self.data.get('tokenised_transcript', None)
    
    @property
    def isocode(self):
        try:
            return self.data.get("ISO Code", None)[0]
        except Exception as e:
            return None
    
    def explain(self, s):  # pragma: no cover
        """A helper to explain what the unicode names for a given string are"""
        for char in s:
            print("%r: %s" % (char, unicodedata.name(char)))
    
    def standardise(self, s):
        """Standardises string data"""
        s = unicodedata.normalize('NFC', s)
        # replace U003A COLON with U02D0 MODIFIER LETTER TRIANGULAR COLON
        s = s.replace(":", "ː")
        # remove special case of DOTTED CIRCLE ◌
        s = s.replace(unicodedata.lookup("DOTTED CIRCLE"), "")
        return s
    
    def read(self, filename):
        """Read `filename`"""
        with codecs.open(filename, 'r', encoding="'utf-8-sig'") as handle:
            section = None
            for line in handle:
                line = line.strip()
                if len(line) == 0:
                    continue
                elif line.startswith("#"):
                    section = self._parse_section(line)
                    self.logger.debug("entered %s" % section)
                    # open section
                    if self.data[section] is None:
                        self.data[section] = []
                elif section:
                    self.data[section].append(line)
        
        # extra handlers
        self._process_standardisation()
        self._choose_transcript(self.preferred_transcript)
        self.known_missings = self.parse_list(self.data['Errors'])
        self.other_symbols = self.parse_list(self.data['Other Symbols'], toktype="other")
        self._process_tokens()
        self._process_orthography()
        return
    
    def parse_inventory(self, inventory, phoneme_type=None):
        """Parse a phoneme inventory"""
        inventory = unicodedata.normalize('NFC', inventory)
        tokens, _buffer = [], []
        IN_ALLOPHONE = False
        if inventory.count("(") != inventory.count(")"):
            raise ValueError("Mismatched braces in %s" % self.filename)
            
        for c in inventory:
            if c == "(":
                # open a new allophone section
                _buffer.append(c)
                IN_ALLOPHONE = True
            elif c == ")":
                # leave allophone
                _buffer.append(c)
                IN_ALLOPHONE = False
                # store to tokens only if allophone section has something
                if len(_buffer):
                    tokens.append("".join(_buffer))  # --> TOKENS
                _buffer = []  # RESET BUFFER
            elif c == " " and IN_ALLOPHONE:
                # inside allophone, just store
                _buffer.append(c)
            elif c in [" ", ","] and not IN_ALLOPHONE:
                # outside allophone and encountered a divider
                # save to tokens if this chunk has anything
                if len(_buffer):
                    tokens.append("".join(_buffer))  # --> TOKENS
                _buffer = []  # RESET BUFFER
            else:
                _buffer.append(c)
        
        # clean up any remainder
        if len(_buffer):
            tokens.append("".join(_buffer))  # --> TOKENS
        return [Token(t, phoneme_type=phoneme_type) for t in tokens]
    
    def _parse_list_block(self, records):
        """
        Helper function to parse list blocks e.g.
        Errors or Other Symbols sections
        """
        out = []
        if records is None:
            return out
        for line in records:
            line = line.strip()
            if self._is_record.match(line):
                token = self._is_record.findall(line)[0].strip()
                out.append(token)
        return out
    
    def parse_list(self, records, toktype="error"):
        """
        Parses a list of lines in `records`. 
        
        If toktype is 'error': Return all tokens as MissingTokens
        If toktype is 'other': Return all tokens as Token set to Other
        """
        if toktype == 'error':
            T = lambda t: MissingToken(t, known_missing=True)
        elif toktype == 'other':
            T = lambda t: Token(t, phoneme_type="other")
        else:
            raise ValueError("Unknown Token Type: %s" % toktype)
            
        return [T(t) for t in self._parse_list_block(records)]
    
    def parse_orthography(self, inventory, phoneme_type=None):
        inventory = unicodedata.normalize('NFC', inventory)
        out = []
        for chunk in inventory.split(","):
            chunk = [_.strip() for _ in chunk.split("=")]
            # grapheme
            orth = self._is_orthography_grapheme.findall(chunk[0])
            orth = Token(*orth, phoneme_type=phoneme_type)
            # phoneme
            phons = []
            for p in chunk[1].split("-"):
                p = self._is_orthography_phoneme.findall(p)
                phons.append(Token(*p, phoneme_type=phoneme_type))
            out.append((orth, phons))
        return out
    
    def get_variants(self):
        """Returns all token variants"""
        if hasattr(self, "_variants"):  # cache
            return self._variants
        sets = [
            self.known_missings, self.default_tokens, self.boundary_tokens,
            self.other_symbols, self.inventory
        ]
        sets = [s for s in sets if s is not None]
        self._variants = {}
        for tok in {i for j in sets for i in j}:
            for v in tok.variants:
                self._variants[v] = tok
        return self._variants
    
    def get_exact(self, char):
        """Returns a list of variants that match token"""
        char = char.raw if isinstance(char, Token) else char
        return [v for v in self.get_variants() if v == char]
    
    def get_possible(self, char):
        """Returns a list of variants that start like token"""
        char = char.raw if isinstance(char, Token) else char
        return [v for v in self.get_variants() if v.startswith(char)]
    
    def get_missing(self, char):
        """
        Helper to return either a Missing Token or a tagged
        KnownMissingToken
        """
        char = char.raw if isinstance(char, Token) else char
        if char in [t.raw for t in self.known_missings]:
            return MissingToken(char, known_missing=True)
        elif char in [t.raw for t in self.default_tokens]:
            return Token(char, phoneme_type="default")
        else:
            return MissingToken(char)
    
    def is_boundary(self, char):
        """Returns True if `char` is one of our boundary characters"""
        char = char.raw if isinstance(char, Token) else char
        return True if char in [t.raw for t in self.boundary_tokens] else False
    
    def is_combining(self, char):
        """Returns True if `char` is one of our combining characters"""
        char = char.raw if isinstance(char, Token) else char
        # short cut if char is already defined in other symbols or inventory
        # (see test_regression.py:test_combining_in_others)
        if char in [_.raw for _ in self.tokens]:
            return False
        return True if char in [_.raw for _ in self.combining_tokens] else False
    
    def get_maximal(self, store):
        """Returns the maximal sub match and the remaining characters that don't match"""
        matched, remainder = None, None
        for i in range(0, len(store) + 1):
            if self.get_exact("".join(store[0:i])):
                matched, remainder = store[0:i], store[i:]
        return matched, remainder

    def parse_transcript(self, transcript):
        variants = self.get_variants()
        transcript = [_ for _ in transcript]
        store, tokens, previous = [], [], []
        self.logger.debug('Transcript: Entering Transcript')
        loopcount = 1
        while len(transcript):
            char = transcript.pop(0)
            self.logger.debug('Transcript: BEGIN Round %d with "%s"' % (loopcount, char))
            
            # join in all combining glyphs, don't span across word boundaries
            if not self.is_boundary(char):
                while len(transcript) and self.is_combining(transcript[0]):
                    char = "%s%s" % (char, transcript.pop(0))
                    self.logger.debug('Transcript: extended with combining to "%s"' % char)
            
            store.append(char)
            
            token = "".join(store)
            exact = self.get_exact(token)
            possible = self.get_possible(token)
            
            if self.is_boundary(char):
                possible = []
            
            self.logger.debug('Transcript: token = "%s"' % token)
            self.logger.debug('Transcript: exact = %r' % exact)
            self.logger.debug('Transcript: possible = %r' % possible)
            
            # 1. exact = 1, no possible future matches.
            if len(exact) == 1 and len(possible) == 0:
                self.logger.debug('Transcript: -> #1 (match, append)')
                tokens.append(variants[exact[0]])
                store, exact, possible = [], [], []  # RESET
            # exact = 1 and possible the same as exact --> perfect mach
            elif len(exact) == 1 and exact == possible:
                self.logger.debug('Transcript: -> #2 (perfect match)')
                tokens.append(variants[exact[0]])
                store, exact, possible = [], [], []  # RESET
            # 3. exact = 1, possible future matches
            elif len(exact) == 1 and len(possible):
                self.logger.debug('Transcript: -> #3 (fallthru)')
                pass  # wait until next round
            # 4. exact = 0, possible future matches
            elif len(exact) == 0 and len(possible):
                self.logger.debug('Transcript: -> #4 (fallthru)')
                pass  # wait until next round
            # 4. exact = 0, no possible future matches
            elif len(exact) == 0 and len(possible) == 0:
                self.logger.debug('Transcript: -> #5 (no matches)')
                # if we used to have an exact match? (previous == 1), then
                # append that token, and reset the store.
                if len(previous) == 1:  # had one previous match
                    self.logger.debug('Transcript: -> #5a (append previous): %r' % previous)
                    tokens.append(variants[previous[0]])
                    transcript.insert(0, char)
                    store = []
                # otherwise then append a missing token.
                else:
                    self.logger.debug('Transcript: -> #5b (append missing)')
                    # find maximally large non-missing component
                    maximal, remainder = self.get_maximal(store)
                    if maximal:
                        self.logger.debug('Transcript: -> #5b1 (append maximal submatch)')
                        tokens.append(variants[maximal[0]])
                        for char in remainder[::-1]:
                            transcript.insert(0, char)
                    elif self.get_exact("".join(store[1:])):
                        self.logger.debug('Transcript: -> #5b2 (append previous missing)')
                        tokens.append(self.get_missing(store.pop(0)))
                        tokens.append(variants["".join(store)])
                    else:
                        self.logger.debug('Transcript: -> #5b3 (append complete missing)')
                        tokens.append(self.get_missing(token))
                    store, exact, possible = [], [], []  # RESET
            else:
                raise RuntimeError("Should not get here")
            
            previous = exact[:]
            self.logger.debug('Transcript: END Round %d: %r' % (loopcount, tokens))
            
            loopcount += 1
            if loopcount > self._max_iterate_length:
                raise SystemExit("Too many iterations -- something is broken")
            
        ## cleanup remainder
        if len(store):
            self.logger.debug('Transcript: Cleanup')
            if len(exact) == 1:
                tokens.append(variants[exact[0]])
            else:
                tokens.append(self.get_missing(token))
        self.logger.debug('Transcript: Done')
        return tokens
    
    def get_words(self):
        """Returns a list of the words in the transcript"""
        word, words = [], []
        for token in self.transcript:
            if token in self.other_symbols:
                continue
            elif token.phoneme_type == 'punctuation':
                if len(word) > 0:
                    words.append(word)
                    word = []
            else:
                word.append(token)
            
        if len(word) > 0:
            words.append(word)
        return words


class BibleFileReader(FileReader):
    """FileReader with Bible Addons"""
    
    def read(self, filename):
        super(BibleFileReader, self).read(filename=filename)
        self.bible_url = self.parse_url('Online Bible')
        return

    def parse_url(self, key):
        """Parses a url from the given `key` in data"""
        for line in self.data.get(key, []):
            if line.startswith('http'):
                return line
    


