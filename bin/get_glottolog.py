#!/usr/bin/env python
#coding=utf-8
# pragma: no cover
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import json
import requests

URL_ISO = "http://glottolog.org/resource/languoid/iso/%s"

def query(iso):
    redir = requests.get(URL_ISO % iso)
    if redir.status_code == 404:
        raise Exception("ISO Code %s not found!" % iso)
    return requests.get("%s.json" % redir.url).json()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Queries glottolog for classification information'
    )
    parser.add_argument("ISO", help='ISO-639-3 Code')
    parser.add_argument("outfile", help='outfile', nargs='?', default=None)
    args = parser.parse_args()
    
    if not args.ISO and len(args.ISO) != 3:
        raise ValueError("Invalid ISO Code")
    
    j = query(args.ISO)
    out = json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))
    
    if args.outfile:
        with open(args.outfile, 'w', encoding="utf-8") as handle:
            handle.writelines(out)
    else:
        print(out)



