#!/usr/bin/env python
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
import statistics

sys.path.append('../../bin')
from tools import get_table

def get_remainder(records, percentage):
    mins, maxs = {}, {}
    for r in records:
        if float(r.PPercent) == 100:
            maxs[r.Language] = int(r.Observed)
        elif float(r.PPercent) == percentage:
            mins[r.Language] = int(r.Observed)
    
    return {
        l: {
            "max": maxs[l], "min": mins[l], "diff": (maxs[l] - mins[l])
        } for l in maxs
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='How many more phonemes do we see after X percent?'
    )
    parser.add_argument("percent", help='percentage', type=float)
    args = parser.parse_args()
        
    differences = get_remainder(get_table('coverage.dat'), args.percent)
    
    for d in differences:
        v = differences[d]
        print("%s\t%3d\t%3d\t%3d" % (
            d.ljust(40), v['min'], v['max'], v['diff']
        ))
    
    values = [differences[d]['diff'] for d in differences]

    print("")
    print("After %0.0f Percent we see:" % args.percent)
    print("* Mean:   %0.2f" % statistics.mean(values))
    print("* Median: %0.2f" % statistics.median(values))
    print("* SD:     %0.2f" % statistics.stdev(values))
