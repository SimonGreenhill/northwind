#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
import re
import unicodedata

PHONEME_TYPES = {
    "consonant": "consonant",
    "consonants": "consonant",
    "C": "consonant",
    "vowel": "vowel",
    "vowels": "vowel",
    "V": "vowel",
    "punctuation": "punctuation",
    "P": "punctuation",
    "stress": "stress",
    "S": "stress",
    "misc": "misc",
    "missing": "missing",
    "combiner": "combiner",
    "tone": "tone",
    "T": "tone",
    "default": "default",
    "unknown": "unknown",
    "other": "other",
}


class TokenException(Exception):
    pass


class Token(object):
    _is_allophone_set = re.compile(r"""\((.*?)\)""")

    def __init__(self, token=None, phoneme_type=None):
        self.allophones = None
        self.is_missing = False
        if token:
            token = unicodedata.normalize("NFC", token)
        self.raw = token
        self.phoneme_type = self._validate_phoneme_type(phoneme_type)
        self.token = self.parse(self.raw)

    def _validate_phoneme_type(self, pt):
        if pt is None:
            return None
        if pt not in PHONEME_TYPES:
            raise ValueError("Unknown phoneme_type: %r" % pt)
        return PHONEME_TYPES[pt]

    def __eq__(self, other):
        return self.raw == other.raw

    def __ne__(self, other):
        return self.raw != other.raw

    def __hash__(self):
        # needed in py3 as anything with __eq__ needs a __hash__ or it'll
        # generate TypeError: unhashable type: 'Token'
        return hash(self.raw)

    def parse(self, token):
        """Parses the token"""
        if token is None:
            return

        if self._is_allophone_set.findall(token):
            allophones = self._is_allophone_set.findall(token)
            if len(allophones) > 1:
                raise TokenException("Can't handle more than one set of allophones")
            # allophones must be separated by commas
            self.allophones = [
                _.strip() for _ in allophones[0].split(",") if _ not in [u" "]
            ]
            token = self._is_allophone_set.sub("", token)
        return token

    @property
    def variants(self):
        """
        Possible variants of this token.
        
        If we have allophones then we get a list of each allophone.
        If we do not have allophones then we get a list of just the token
        """
        variants = []
        if self.allophones:
            for a in self.allophones:
                variants.append(a)
            if self.token not in variants:
                variants.append(self.token)
        else:
            variants.append(self.token)
        return variants

    @property
    def names(self):
        """Gives unicode names for token"""
        out = [unicodedata.name(_) for _ in self.token]
        if self.allophones:
            for a in self.allophones:
                out.extend([unicodedata.name(_) for _ in a])
        return out

    def __repr__(self):
        if self.allophones is not None:
            out = "<%s(%s)>" % (self.token, u", ".join(self.allophones))
        else:
            out = "<%s>" % self.token
        return out

    def debug(self):  # pragma: no cover
        print("Raw: %r" % self.raw)
        print("Token: %r" % self.token)
        print("Allophones: %r" % self.allophones)


class MissingToken(Token):
    """Missing Token"""

    def __init__(self, token=None, phoneme_type="missing", known_missing=False):
        super(MissingToken, self).__init__(token=token, phoneme_type=phoneme_type)
        self.is_missing = True
        self.known_missing = known_missing

    def __repr__(self):
        if self.known_missing:
            return "<KnownMissingToken: %s>" % self.raw
        else:
            return "<MissingToken: %s>" % self.raw
