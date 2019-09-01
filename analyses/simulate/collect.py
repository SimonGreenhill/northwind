#!/usr/bin/env python3
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2018 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
import sys
import codecs
from collections import namedtuple
sys.path.append('../../bin/')
from tools import remove_accents

from make import RESULTSDIR

def get_table(filename):
    Record = namedtuple("Record", ["Language", "Replicate", "Length"])
    with codecs.open(filename, 'r', encoding="utf8") as handle:
        for line in handle:
            yield Record(*[_.strip() for _ in line.split("\t")])


if __name__ == '__main__':
    files = [
        f for f in os.listdir(RESULTSDIR) if f.endswith('.dat')
    ]
    with codecs.open("results.txt", 'w', 'utf8') as output:
        output.write("Language\tReplicate\tLength\tType\n")
        for filename in files:
            for rec in get_table(os.path.join(RESULTSDIR, filename)):
                output.write("\t".join([
                    remove_accents(rec.Language),  # to match predict-gam
                    rec.Replicate,
                    rec.Length,
                    'Simulated'
                ]))
                output.write("\n")
        
