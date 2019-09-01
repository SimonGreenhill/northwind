#!/usr/bin/env python3
# coding=utf-8

import os
import sys
import logging
sys.path.append('../../bin')

from tools import BibleFileReader

#logging.basicConfig(level=logging.DEBUG)
from lib import JIPA_DIR, BIBLE_DIR, SOURCE_DIR, collect_bibles

if __name__ == '__main__':

    bibles = collect_bibles()

    # we've got a mismatch for Estonian -- ISO code est (Estonian 
    # macrolanguage) vs ekk (Standard Estonian), so make sure both
    # are available.
    bibles['ekk'] = bibles['est']


    print("Language\tBible")
    for filename in os.listdir(JIPA_DIR):
        try:
            b = BibleFileReader(os.path.join(JIPA_DIR, filename))
        except Exception as e:
            sys.stdout.write("ERROR: Unable to load - %s - %s\n" % (filename, e))
            continue

        if not hasattr(b, 'orthography'):
            sys.stdout.write("ERROR: No orthography - %s\n" % filename)
            continue

        elif b.bible_url is None:
            # can be safely skipped
            # sys.stdout.write("No Bible URL - %s\n" % filename)
            continue
        
        elif not bibles.get(b.isocode):
            sys.stdout.write("ERROR: No bible found - %s\n" % filename)
            continue

        else:
            for bible in bibles.get(b.isocode):
                print("%s\t%s" % (filename, bible))
            print("")
