#!/usr/bin/env python
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
import codecs

sys.path.append('../../bin')
from tools import load_data, remove_accents, get_cumulative_coverage, get_table

if __name__ == '__main__':
    glottolog = {
        r.Language: r.Family for r in
        get_table('../../data/glottolog/glottolog.dat')
    }
    
    with codecs.open('coverage.dat', 'w', encoding="utf-8") as handle:
        handle.write("\t".join([
            'Language',
            'Family',
            'ISOCode',
            'Position',
            'PPercent',
            'Observed',
            'OPercent',
            'TotalInventory',
            'TranscriptLength',
        ]))
        handle.write("\n")
        
        for f in load_data():
            results = get_cumulative_coverage(f)
            family = glottolog[f.language]
            for r in results:
                handle.write("\t".join([
                    remove_accents(r.language),
                    family,
                    r.isocode,
                    '%d' % r.position,
                    '%0.3f' % r.ppercent,
                    '%d' % r.observed,
                    '%0.3f' % r.opercent,
                    '%d' % r.total_inv,
                    '%d' % len(r.transcript),
                ]))
                handle.write("\n")

