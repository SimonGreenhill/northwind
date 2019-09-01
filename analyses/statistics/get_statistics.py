#!/usr/bin/env python
#coding=utf-8
#pragma: no cover
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
import codecs

sys.path.append('../../bin')
from tools import load_data, get_table, get_audio, remove_accents, safe_name

header = [
    "FullLanguage",
    "Language",
    "Label",
    "Family",
    "InventoryLength",
    "Tokens",
    "TranscriptLength",
    "AudioLength",
    "Unobserved",
    "Errors",
    "DistinctErrors",
]
    
def describe(f, glottolog):
    audio = get_audio(f.data.get('Audio'))
    return {
        "FullLanguage": f.language,
        "Language": remove_accents(f.language),
        "Label": safe_name(remove_accents(f.language)),
        "Family": remove_accents(glottolog.get(f.language)),
        "InventoryLength": '%d' % len(f.inventory),
        "Tokens": '%d' % len(f.tokens),
        "TranscriptLength": '%d' % len(f.transcript),
        "AudioLength": 'NA' if audio is None else '%d' % audio,
        "Unobserved": '%d' % len(f.unobserved),
        "Errors": '%d' % len(f.errors),
        "DistinctErrors": '%d' % len(set(f.errors)),
    }
    

if __name__ == '__main__':
    glottolog = get_table('../../data/glottolog/glottolog.dat')
    glottolog = {r.Language: r.Family for r in glottolog}
    print("\t".join(header))
    for f in load_data():
        summary = describe(f, glottolog)
        print("\t".join([summary[h] for h in header]))
