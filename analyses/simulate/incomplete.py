#!/usr/bin/env python3
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2018 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os

from make import DATADIR, RESULTSDIR


if __name__ == '__main__':
    for filename in sorted(os.listdir(DATADIR)):
        if not filename.endswith(".txt"):
            continue
            
        log = "%s.dat" % os.path.join(
            RESULTSDIR, os.path.splitext(filename)[0]
        )
        if not os.path.isfile(log):
            print("Missing results for %s" % filename)
