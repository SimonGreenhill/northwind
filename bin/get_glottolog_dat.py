#!/usr/bin/env python
#coding=utf-8
"""Create glottolog datafile"""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
import sys
import json
import codecs

from tools import load_data

# Locations for places that don't have any (lat, long)
LOCATIONS = {
    'npi': (27.7, 85.316667),
    'nuk': (54, -125),
    
}

columns = [
    'ID', 'ISO', 'Language', 'Family', 'Latitude', 'Longitude', 'Classification'
]


def get_values(filename):
    with codecs.open(filename, 'r', encoding="utf-8") as handle:
        j = json.load(handle)
    classif = get_classification(j['classification'])
    if len(classif) == 0:
        classif = [j['name']]
        
    return {
        'ID': j['id'],
        'ISO': j['iso639-3'],
        'Latitude': j['latitude'],
        'Longitude': j['longitude'],
        'Family': classif[0],
        'Classification': ", ".join(classif),
    }

def get_classification(clades, type="name"):
    return [c.get(type) for c in clades]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Constructs a glottolog data file'
    )
    parser.add_argument("datadir", help="datadir with all glottolog files")
    parser.add_argument("outputfile", help="output file")
    args = parser.parse_args()
    
    files = [f for f in os.listdir(args.datadir) if f.endswith('.json')]
    
    glottodata = {}
    for filename in files:
        iso = os.path.splitext(filename)[0]
        glottodata[iso] = get_values(os.path.join(args.datadir, filename))
    
    with open(args.outputfile, 'w', encoding="utf-8") as handle:
        handle.write("\t".join(columns))
        handle.write("\n")
        for f in load_data():
            iso = f.data['ISO Code'][0]
            r = glottodata[iso]
            # add extras
            r['Language'] = f.language
            if iso in LOCATIONS:
                r['Latitude'], r['Longitude'] = LOCATIONS[iso]
            
            handle.write("\t".join([str(r[c]) for c in columns]))
            handle.write("\n")


