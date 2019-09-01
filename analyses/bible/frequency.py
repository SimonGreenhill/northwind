#!/usr/bin/env python3
# coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2019 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
import codecs

# import logging
# logging.basicConfig(level=logging.DEBUG)

sys.path.append('../../bin')

from tools import BibleFileReader
from lib import tally_bible


def write(content, filename):
    with codecs.open(filename, 'w', 'utf8') as handle:
        handle.write("Token\tCount\tType\tMissing\n")
        for k in content.most_common():
            handle.write("\t".join([
                format_token(k[0]),
                '%d' % k[1],
                k[0].phoneme_type,
                'TRUE' if k[0].is_missing else 'FALSE',
            ]))
            handle.write("\n")


def format_token(token):
    if token.is_missing:
        return repr(token).split(": ")[1][0:-1]
    else:
        return repr(token)[1:-1]




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Outputs token frequency')
    parser.add_argument("filename", help='JIPA Article filename')
    parser.add_argument("bible", help='bible filename')
    parser.add_argument(
        '-o', "--output", dest='output',
        help="specify output file",
        action='store'
    )
    args = parser.parse_args()

    bf = BibleFileReader(args.filename)
    if not bf.orthography:
        raise ValueError("No orthography for this language")
    write(tally_bible(bf, args.bible), args.output)

