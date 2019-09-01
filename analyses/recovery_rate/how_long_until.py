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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='How long until we\'ve seen X percent?'
    )
    parser.add_argument("percent", help='percentage', type=float)
    args = parser.parse_args()
        
    records = get_table('statistics.dat')
    # OPercent = observed percentage
    # Ppercent = position in transcript as percentage
    records = [r for r in records if float(r.OPercent) == args.percent]
    print(records)
    observedPc = [float(r.PPercent) for r in records]
    observedPh = [float(r.Position) for r in records]

    print("Time to %0.2f%% coverage" % args.percent)
    print("* Mean:   %0.2f" % statistics.mean(observedPc))
    print("* Median: %0.2f" % statistics.median(observedPc))
    print("* SD:     %0.2f" % statistics.stdev(observedPc))

    print("Position of %0.2f%% coverage" % args.percent)
    print("* Mean:   %0.2f" % statistics.mean(observedPh))
    print("* Median: %0.2f" % statistics.median(observedPh))
    print("* SD:     %0.2f" % statistics.stdev(observedPh))
