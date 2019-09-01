#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
import re

from .Token import Token


class OrthemeException(Exception):
    pass

# <ô>=/ɔː/
#     # orthographies with overlapping forms e.g.
#     # <s> = /s/-/ʃ/
#     # -> s in the orthgraphy could mean /s/ or /ʃ/ phoneme
class Ortheme(object):
    _is_grapheme = re.compile(r"""<(.*)>""")
    _is_phoneme = re.compile(r"""/(.*)/""")

    def __init__(self, chunk=None, phoneme_type=None, inventory=None):
        self.raw = chunk
        self.phoneme_type = phoneme_type
        self.graphemes = []
        self.phonemes = []
        self.parse(chunk)
        if inventory:
            self.match_inventory(inventory)

    def __eq__(self, other):
        return self.graphemes == other.graphemes and self.phonemes == other.phonemes

    def __repr__(self):
        return "%s = %s" % (
            "-".join("%s" % t for t in self.graphemes),
            "-".join(
                ("%s" % t).replace("<", "/").replace(">", "/") for t in self.phonemes
            ),
        )

    def parse(self, chunk):
        """
        Parses the Orthographic mapping.

        Returns a tuple of lists([graphemes], [phonemes])
        """
        if "=" not in chunk:
            raise OrthemeException("Invalid format for chunk (no =) %s" % self.raw)
        chunk = [_.strip() for _ in chunk.split("=")]
        if len(chunk) != 2:
            raise OrthemeException("Invalid Ortheme %s" % self.raw)

        # parse graphemes
        for g in chunk[0].split("-"):
            g = self._is_grapheme.findall(g)
            self.graphemes.append(Token(*g, phoneme_type=self.phoneme_type))

        # parse phonemes
        for p in chunk[1].split("-"):
            p = self._is_phoneme.findall(p)
            self.phonemes.append(Token(*p, phoneme_type=self.phoneme_type))
        return (self.graphemes, self.phonemes)

    def match_inventory(self, inventory):
        # get short forms
        shorts = {}
        for p in inventory:
            shorts[p.token] = p
            if p.allophones:
                shorts.update({a: p for a in p.allophones})

        for i, p in enumerate(self.phonemes):
            if p in inventory:
                continue
            # is this a short match i.e. no allophones and matches the 
            # token only?
            # if so, convert the phoneme to the correct form.
            elif not p.allophones and p.token in shorts:
                self.phonemes[i] = shorts[p.token]
            # error
            else:
                raise ValueError("%s is not in inventory" % p)
