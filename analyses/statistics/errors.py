#!/usr/bin/env python
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
sys.path.append('../../bin')
from tools import load_data

if __name__ == '__main__':
    for f in load_data():
        errors = f.data.get('Errors', None)
        if errors and len(errors):
            for e in errors:
                print("\t".join([f.language, e]))
