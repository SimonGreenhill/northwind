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

from lib import read_bible
from tools import BibleFileReader
from tools.misc import CoverageResult

# ../bin.misc.get_cumulative_coverage rewritten to handle the large 
# bible corpora i.e.
#   - only logs instances where percentage seen has changed
#   - doesn't store transcript to save blowing out our RAM
#   - runs off a generator from `read_bible` (so doesn't need the 
#     full transcript loaded in RAM first.
def get_cumulative_coverageLarge(reader_obj, biblefile, log=True):
    """
    Returns a list of values describing the cumulative coverage of a
    given `reader_obj`.
    """
    # how many characters do we need to see?
    observed_inventory = len(reader_obj.inventory)
    
    # the results list that gets returned
    out = []
    # the distinct characters seen until now
    distinct_chars = set()
    # the position in the text (i.e. transcript length)
    pos = 0
    # the last seen position that we updated (used to save excess logging)
    last_seen = 0
    for i, (_, line) in enumerate(read_bible(biblefile), 1):
        if log:  # pragma: no cover
            sys.stdout.write("\r%6d" % i)
            sys.stdout.flush()
        
        for char in reader_obj.toIPA(line):
            pos += 1
            distinct_chars.add(char)
            # get seen characters to this point
            seen = set(c for c in reader_obj.inventory if c in distinct_chars)

            # only output if there's a change.
            if len(seen) != last_seen:
                last_seen = len(seen)
                out.append(
                    CoverageResult(
                        language=reader_obj.language,
                        isocode=reader_obj.isocode,
                        position=pos,
                        ppercent="NA",
                        observed=len(seen),
                        opercent=(len(seen) / observed_inventory) * 100,
                        total_inv=observed_inventory,
                        transcript="NA",
                        transcript_length=pos
                    )
                )
                if log:  # pragma: no cover
                    sys.stdout.write("\r\n")
                    sys.stdout.write(repr(out[-1]))
                    print(reader_obj.parse_transcript.cache_info())
                    sys.stdout.write("\n")
                    sys.stdout.flush()

    # and finally
    out.append(
        CoverageResult(
            language=reader_obj.language,
            isocode=reader_obj.isocode,
            position=pos,
            ppercent="NA",
            observed=len(seen),
            opercent=(len(seen) / observed_inventory) * 100,
            total_inv=observed_inventory,
            transcript="NA",
            transcript_length=pos,
        )
    )
    return out



def write(reader, results, filename):  # pragma: no cover
    with codecs.open(filename, 'w', 'utf8') as handle:
        handle.write("\t".join([
            'Language',
            'ISOCode',
            'Position',
            'PPercent',
            'Observed',
            'OPercent',
            'TotalInventory',
            'TranscriptLength',
        ]))
        handle.write("\n")
        for r in results:
            handle.write("\t".join([
                reader.language,
                reader.isocode,
                '%d' % r.position,
                r.ppercent,
                '%d' % r.observed,
                '%0.3f' % r.opercent,
                '%d' % r.total_inv,
                '%d' % len(r.transcript),
            ]))
            handle.write("\n")


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
    results = get_cumulative_coverageLarge(bf, args.bible)
    write(bf, results, args.output)

