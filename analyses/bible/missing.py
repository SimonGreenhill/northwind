#!/usr/bin/env python3
# coding=utf-8
"""..."""
import os
import sys
sys.path.append('../../bin')
from tools import BibleFileReader, Token, get_table
from lib import BIBLE_DIR, JIPA_DIR

if __name__ == '__main__':
    print("Bible\tLanguage\tToken\tCount")
    for row in get_table('bibles.txt'):
        if row.Language.startswith("#"):
            continue

        bible = os.path.join(BIBLE_DIR, row.Bible)
        jipa = BibleFileReader(os.path.join(JIPA_DIR, row.Language))
        outfreq = row.Bible.replace(".txt", ".freq")

        freq = {
            r.Token: r.Count for r in get_table(outfreq)
        }
        for token in jipa.inventory:
            print("\t".join([
                row.Bible,
                row.Language,
                token.raw,
                str(freq.get(token.raw, '???'))
            ]))


