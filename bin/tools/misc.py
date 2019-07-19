#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import codecs
import unicodedata
from collections import namedtuple

from .FileReader import FileReader

DATADIR = os.path.join(
    os.path.split(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])[0], 'data'
)


def remove_accents(input_str):  # I hate having to do this
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def load_data(datadir=DATADIR):
    """Loads the data"""
    datafiles =  sorted([
        os.path.join(datadir, f) for f in os.listdir(datadir) if f.endswith('.txt')
    ])
    for f in datafiles:
        yield FileReader(f)
    

def get_table(filename):
    Record = None
    with codecs.open(filename, 'r', encoding="utf8") as handle:
        for line in handle:
            line = [_.strip() for _ in line.split("\t")]
            if not Record:
                Record = namedtuple("Record", line)
            else:
                yield Record(*line)


def safe_name(var):
    """Returns a theoretically 'safe' language name used for nexus files etc"""
    var = remove_accents(var)
    return var.replace("(", "").replace(")", "").replace(" ", "_").replace("-", "")


def get_cumulative_coverage(reader_obj):
    """
    Returns a list of values describing the cumulative coverage of a
    given `reader_obj`.
    """
    Result = namedtuple("Result", [
        "language", "isocode",
        "position", "ppercent", "observed", "opercent", "total_inv",
        "transcript", "transcript_length"
    ])
    
    observed_inventory = len(reader_obj.inventory)
    
    out = []
    one_pc = len(reader_obj.transcript) / 100
    transcript_length = len(reader_obj.transcript)
    for ppercent in range(0, 101, 1):
        # calculate position in characters
        pos = round(one_pc * ppercent)
        # get seen characters to this point
        transcript = reader_obj.transcript[0:pos]
        # how many have we seen?
        seen = set(c for c in reader_obj.inventory if c in transcript)
        out.append(Result(
            language=reader_obj.language,
            isocode=reader_obj.isocode,
            position=pos,
            ppercent=ppercent,
            observed=len(seen),
            opercent=(len(seen) / observed_inventory) * 100,
            total_inv=observed_inventory,
            transcript=transcript,
            transcript_length=transcript_length
        ))
    return out


def get_audio(var):
    if var is None:
        return None
    var = [v for v in var if len(v)]
    
    if not len(var):
        return None
    if var[0] == 'NA':
        return None
    
    try:
        return float(var[0])
    except:
        raise ValueError("Unknown Audio: %r" % var)
    
    
    