#!/usr/bin/env python
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
import statistics
from collections import Counter

sys.path.append('../../bin')
from tools import load_data, get_table

GLOTTOLOG_DATA = "../../data/glottolog/glottolog.dat"

TEMPLATE = """
# Statistics

* Number of Inventories: %(ninventories)d
* Number of Languages: %(nlanguages)d
* Number of Publications: %(npubs)d

## Length of Inventory:

* Range: %(imin)d - %(imax)d
* Median: %(imedian)f
* SD: %(isd)f

## Length of Full Token Inventory:

(i.e. inventory + missing + other_symbols)

* Range: %(fmin)d - %(fmax)d
* Median: %(fmedian)f
* SD: %(fsd)f

## Length of Transcript:

* Range: %(tmin)d - %(tmax)d
* Median: %(tmedian)f
* SD: %(tsd)f



## Languages by Family:

%(lbf)s

"""

def lbf(families):  # pragma: no cover
    out = []
    total = sum(families.values())
    for f in families.most_common():
        pc = (f[1] / total) * 100
        out.append("* %d (%0.2f) - %s" % (f[1], pc, f[0]))
    return "\n".join(out)

if __name__ == '__main__':
    records = {r.ISO: r for r in get_table(GLOTTOLOG_DATA)}
    
    families = Counter()
    languages, inventories, tokens, transcripts, references = set(), [], [], [], set()
    for ninv, f in enumerate(load_data(), 1):
        languages.add(f.isocode)
        inventories.append(len(f.inventory))
        tokens.append(len(f.tokens))
        transcripts.append(len(f.transcript))
        
        references.add(f.data['Reference'][0])
        
        g = records.get(f.isocode, None)
        assert g is not None, "Unknown ISO code: %s" % f.isocode
        families[g.Family] += 100
    
    print(TEMPLATE % {
        'ninventories': ninv,
        'nlanguages': len(languages),
        'npubs': len(references),
        # Inventories
        'imin': min(inventories),
        'imax': max(inventories),
        'imedian': statistics.median(inventories),
        'isd': statistics.stdev(inventories),
        # Full Inventories
        'fmin': min(tokens),
        'fmax': max(tokens),
        'fmedian': statistics.median(tokens),
        'fsd': statistics.stdev(tokens),
        # Transcripts:
        'tmin': min(transcripts),
        'tmax': max(transcripts),
        'tmedian': statistics.median(transcripts),
        'tsd': statistics.stdev(transcripts),
        # Other
        'lbf': lbf(families),
    })
