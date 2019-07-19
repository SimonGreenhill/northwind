#!/usr/bin/env python
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
import codecs

try:
    from treemaker import TreeMaker
except ImportError:
    raise ImportError("Please install treemaker")

from tools import get_table, safe_name

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Constructs a tree from the glottolog data file'
    )
    parser.add_argument("glottfile", help='Glottolog data file')
    parser.add_argument("treefile", help='Treefile to save as')
    args = parser.parse_args()
    
    if not os.path.isfile(args.glottfile):
        raise IOError("File %s not found" % args.glottfile)
    
    t = TreeMaker()
    t.add_from((safe_name(o.Language), o.Classification) for o in get_table(args.glottfile))
    t.write_to_file(args.treefile)



