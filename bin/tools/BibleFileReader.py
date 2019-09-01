#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8

import unicodedata
from functools import lru_cache
from .Token import Token
from .Ortheme import Ortheme
from .FileReader import FileReader


class BibleFileReader(FileReader):
    """FileReader with Bible Addons"""

    @property
    def orthography(self):
        return self.data.get("orthography_consonants", []) + self.data.get(
            "orthography_vowels", []
        )

    def read(self, filename):
        super().read(filename=filename)
        self.bible_url = self.parse_url("Online Bible")
        self._process_orthography()
        return

    def _process_orthography(self):
        """Process Orthography blocks"""
        OCPC = "Orthography Consonant Phoneme Correspondences"
        OVPC = "Orthography Vowel Phoneme Correspondences"

        self.data["orthography_vowels"] = self.data.get("orthography_vowels", [])
        self.data["orthography_consonants"] = self.data.get(
            "orthography_consonants", []
        )
        self.data["orthography"] = self.data.get("orthography", [])
        
        if self.data[OCPC]:
            self.logger.debug("parse_inventory:orthography_consonants")
            self.data[OCPC] = [self.standardise(l) for l in self.data.get(OCPC, [])]
            self.data["orthography_consonants"] = self.parse_orthography(
                self.join(self.data[OCPC]), "consonant"
            )

        if self.data[OVPC]:
            self.logger.debug("parse_inventory:orthography_vowels")
            self.data[OVPC] = [self.standardise(l) for l in self.data.get(OVPC, [])]
            self.data["orthography_vowels"] = self.parse_orthography(
                self.join(self.data[OVPC]), "vowel"
            )
        return

    def parse_orthography(self, inventory, phoneme_type=None):
        inventory = unicodedata.normalize("NFC", inventory)
        out = []
        for chunk in inventory.split(","):
            chunk = chunk.strip()
            # these sections have commas replaced with "." to stop misparsing.
            chunk = chunk.replace('.', ',')
            if len(chunk):
                try:
                    o = Ortheme(chunk, phoneme_type, inventory=self.inventory)
                except ValueError:  # pragma: no cover
                    print('Unable to find %s in inventory' % chunk)
                out.append(o)
        return out

    def parse_url(self, key):
        """Parses a url from the given `key` in data"""
        content = self.data.get(key, [])
        content = content if content else []  # handle case when data[key] is None
        for line in content:
            if line.startswith("http"):
                return line
        return None  # pragma: no cover

    def get_variants(self):
        """Returns all token variants"""
        # insert orthemes...
        # possibilities:
        # 1:1: <a> = /x/      = simple, grapheme a = phoneme x
        # n:1: <a>-<b> = /x/  = multiple graphemes (a,b), one phoneme x
        # n:n: <a> = /x/-/y/  = graphemes to multiple phonemes (x, y)
        #    -> this latter case is problematic as we can't capture it in this parsing
        #    system. Have to handle later.
        variants = super().get_variants()
        for o in self.orthography:
            # handle the n:n case by taking the first phoneme
            if len(o.phonemes) > 1:
                self.logger.debug("get_variants:orthography:n-n case: %r" % o)
            replacement = o.phonemes[0]

            # loop over all things in graphemes (usually 1, but could be n)
            for tok in o.graphemes:
                for v in tok.variants:  # add all variants
                    variants[v] = replacement
        return variants
        
    @lru_cache(maxsize=1024)
    def parse_transcript(self, text):
        # this is only overridden here for the lru_caching. i.e. I don't want to
        # mess with the simplicity of the base FileReader
        return super().parse_transcript(text)
        
    def toIPA(self, text):
        out = []
        for chunk in text.split(" "):
            out.extend(self.parse_transcript(chunk.lower()))
            out.append(Token(" ", 'punctuation'))
        out.pop() # remove unnecessary trailing token
        return out
        #return self.parse_transcript(text.lower())
