#!/usr/bin/env python
#coding=utf-8
# pragma: no cover
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2014 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
import codecs
import warnings
import unicodedata
from tools import FileReader
from tools.misc import get_audio

import logging
logging.basicConfig(filename='check.log', level=logging.DEBUG)


DATADIR = "../data/"

class Checker(object):
    error_count = 0
    must_have_fields = [
        'Reference',
        'Language',
        'ISO Code',
        'Consonant Inventory',
        'Vowel Inventory',
        'Transcript',
        'vowels',
        'consonants',
        'tokenised_transcript',
    ]
    
    def check(self, filename, extended=False):
        with warnings.catch_warnings(record=True) as self.warnings:
            warnings.simplefilter("always")
            self.F = FileReader(filename)
        
        self.checks = {
            'warnings': self.check_warnings(filename),
            'unicode': self.check_unicode(filename),
            'data': self.check_data(filename),
            'iso': self.check_iso(filename),
            'tonemes': self.check_toneme_inventory(filename),
            'audio': self.check_audio(filename),
        }
        if extended:
            self.checks['orthography'] = self.check_orthography(filename)
            self.checks['minimalpairs'] = self.check_mp(filename)
        return self
    
    def is_missing(self, field):
        #if field == 'Reference' and self.F.filename == "./Basaa.txt":
            #import IPython; IPython.embed();
        if self.F.data[field] is None:
            return True
        elif len(self.F.data[field]) == 0:
            return True
        else:
            return False
    
    def check_unicode(self, filename):
        errors = []
        with codecs.open(filename, 'rU', encoding="utf-8") as handle:
            for i, line in enumerate(handle.readlines(), 1):
                line = line.strip().replace(" ", "")
                for j, char in enumerate(line, 1):
                    try:
                        unicodedata.name(char)
                    except ValueError:
                        errors.append("line %d:%d %s %r" % (i, j, char, char))
        return errors
    
    def check_warnings(self, filename):
        return [w.message for w in self.warnings]
    
    def check_data(self, filename):
        errors = []
        for field in self.must_have_fields:
            if self.is_missing(field):
                errors.append("Missing %s" % field)
        return errors
    
    def check_iso(self, filename):
        if self.F.data['ISO Code'] is None:
            return []  # checked elsewhere
        if len(self.F.data['ISO Code']) == 0:
            return []  # checked elsewhere
        if len(self.F.data['ISO Code'][0]) != 3:
            return [
                "ISO Code is not 3 characters: %r" % self.F.data['ISO Code']
            ]
        return []
    
    def check_toneme_inventory(self, filename):
        if 'Tonemes' in self.F.data:
            return ['should be toneme inventory']
        if 'Toneme inventory' in self.F.data and len(self.F.data['tones']) == 0:
            return ['no tones']
        return []

    def check_audio(self, filename):
        if 'Audio' not in self.F.data:
            return ['No Audio Block']
        if self.F.data['Audio'] is None:
            return ['No Audio']
        try:
            get_audio(self.F.data['Audio'])
        except:
            return ['Audio parsing error']
        return []

    def check_orthography(self, filename):
        errors = []
        if self.is_missing('orthography_vowels'):
            errors.append("No orthography_vowels")
        if self.is_missing('orthography_consonants'):
            errors.append("No orthography_consonants")
        if self.is_missing('orthography'):
            errors.append("No orthography")
        return errors
    
    def check_mp(self, filename):
        errors = []
        if self.is_missing("Minimal Pairs"):
            errors.append("No Minimal Pairs")
        if self.is_missing("Minimal Pair Examples"):
            errors.append("No Minimal Pair Examples")
        return errors
    
    def result(self, filename=None, quiet=True):
        errors = sum([len(self.checks[check]) for check in self.checks])
        self.error_count += errors
        
        if errors > 0:
            print("ERROR %s:" % filename)
            for check in sorted(self.checks):
                if len(self.checks[check]):
                    for e in self.checks[check]:
                        print("\t%s - %s" % (check.ljust(20), e))
            return False
        else:
            if not quiet:
                print("OK    %s:" % filename.ljust(60))
        
        return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Checks Data Directory')
    parser.add_argument("path", help="directory or filename")
    parser.add_argument(
        '-x', "--extended", dest='extended',
        help="Extended check (orthography etc)", action='store_true'
    )
    args = parser.parse_args()
    C = Checker()
    if os.path.isdir(args.path):
        filecount = 0
        for filename in os.listdir(args.path):
            if filename.endswith('.txt'):
                filename = os.path.join(args.path, filename)
                C.check(filename, args.extended).result(filename)
                filecount += 1
        
        print("")
        print("Errors: %d" % C.error_count)
        print("Total Files: %d" % filecount)
    elif os.path.isfile(args.path):
        C.check(args.path, args.extended).result(args.path)
    else:
        raise ValueError("Don't know what to do with %d" % args.path)
