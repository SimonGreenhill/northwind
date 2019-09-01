#!/usr/bin/env python3
# coding=utf-8
"""..."""
import os
import sys
sys.path.append('../../bin')
from tools import get_table

from lib import BIBLE_DIR, JIPA_DIR

CMDfreq = "python frequency.py"
CMDrate = "python rate.py"

if __name__ == '__main__':
    for row in get_table('bibles.txt'):
        if row.Language.startswith("#"):
            continue

        bible = os.path.join(BIBLE_DIR, row.Bible)
        jipa = os.path.join(JIPA_DIR, row.Language)
        outfreq = row.Bible.replace(".txt", ".freq")
        outrate = row.Bible.replace(".txt", ".rate")
        
        if not os.path.isfile(outfreq):
            print(
                '%s "%s" "%s" --output "%s"' % (CMDfreq, jipa, bible, outfreq)
            )

        if not os.path.isfile(outrate):
            print(
                '%s "%s" "%s" --output "%s"' % (CMDrate, jipa, bible, outrate)
            )
