#!/usr/bin/env python3
# coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2019 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
import logging
logging.basicConfig(level=logging.DEBUG)

sys.path.append('../../bin')

from tools import BibleFileReader


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Outputs token frequency')
    parser.add_argument("filename", help='JIPA Article filename')
    args = parser.parse_args()

    bf = BibleFileReader(args.filename)
    for k in bf.data:
        print(k)
        print(bf.data[k])
        print("")

    print("")
    print("@bible_url:")
    print(bf.bible_url)
    print("")
    print("@orthography:")
    print(bf.orthography)

