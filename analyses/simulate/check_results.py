#!/usr/bin/env python3
# coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2018 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
import codecs
from collections import Counter
from make import DATADIR, RESULTSDIR


def read(filename):
    with codecs.open(filename, 'r', 'utf8') as handle:
        for line in handle:
            yield line


def check_err(filename):

    skip = [
        'Traceback (most recent call last):',
        'File ',
        'self.sgt =',
        'sys.stdout.write(',
        'File "simulate.py", line 75, in simulate',
        'raise StopIteration("Abort Abort!")',
        'StopIteration: Abort Abort!',
        "'bins parameter must not be less than %d=freqdist.B()+1'",
        'simulate.py:35: UserWarning:',
        'did not find a proper best fit line',
        'UserWarning: no hapaxes present',
    ]

    def skip_this(line):
        line = line.strip().lstrip()
        for s in skip:
            if line.startswith(s):
                return True
        return False

    errors = []
    for line in read(filename):
        if len(line.strip()) == 0:
            continue
        elif "warnings.warn('SimpleGoodTuring did not find a proper" in line:
            errors.append("SLOPE>-1")  # https://github.com/nltk/nltk/pull/938
        elif 'UserWarning: SimpleGoodTuring did not find a proper best fit line for smoothing probabilities of occurrences' in line:
            continue  # as above
        elif 'warnings.warn("no hapaxes present' in line:
            errors.append("HAPAX CONVERSION")
        elif 'UserWarning: no hapaxes present' in line:
            continue  # as above
        elif 'warnings.warn("no unseen present' in line:
            errors.append("NO UNSEEN")
        elif skip_this(line):
            continue
        else:
            print("EXTRA?", line)
            errors.append("EXTRA?")
    return errors


def check_dat(filename, expected=1000):
    expected = list(range(1, expected + 1))
    for line in read(filename):
        i = int(line.split("\t")[1])
        assert i in expected
        expected.remove(i)
    if len(expected):
        return ['Incomplete']
    return []


if __name__ == '__main__':

    expected = [f for f in os.listdir(DATADIR) if f.endswith('.txt')]
    ecount = Counter()
    good = 0
    for e in sorted(expected):
        language = os.path.splitext(e)[0]
        errors = []
        datfile = os.path.join(RESULTSDIR, "%s.dat" % language)
        errfile = os.path.join(RESULTSDIR, "%s.err" % language)

        # check dat file
        if not os.path.isfile(datfile):
            errors.append("NO RESULTS")
        else:
            errors.extend(check_dat(datfile))

        # check error file
        if os.path.isfile(errfile):
            errors.extend(check_err(errfile))
        
        ecount.update(errors)

        print("%50s\t%s" % (language, ", ".join(errors)))
        
        if not errors:
            good += 1

    print("")
    print("%d/%d" % (good, len(expected)))
    print(ecount)