#!/usr/bin/env python3
# coding=utf-8
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2018 Simon J. Greenhill'
__license__ = 'New-style BSD'

import sys
import warnings
from collections import Counter

import numpy as np
from nltk.probability import FreqDist, SimpleGoodTuringProbDist

sys.path.append('../../bin')
from tools import FileReader


DEBUG = False

STOP = 1e8


class Simulator(object):
    def __init__(self, reader):
        self.reader = reader
        self.freqdist = FreqDist(reader.transcript)
        self.tokens = set(reader.inventory) | set(self.freqdist)
        
        while not self.freqdist.hapaxes():
            warnings.warn("no hapaxes present -- shifting distribution down")
            for k in self.freqdist:
                self.freqdist[k] -= 1

        if min(self.freqdist.values()) != 0:
            warnings.warn("no unseen present -- adding dummy category")
            self.tokens.add("<dummy>")

        if DEBUG:
            import IPython; IPython.embed()

        self.sgt = SimpleGoodTuringProbDist(
            self.freqdist, bins=len(self.tokens)
        )
        self._get_probabilities()

    def _get_probabilities(self):
        self.probabilities = {}
        for t in self.tokens:
            self.probabilities[t] = self.sgt.prob(t)
        return self.probabilities

    def dump(self):
        for t in self.tokens:
            print("\t".join([
                "%30s" % t, '%d' % self.freqdist[t],
                '%0.4f' % self.sgt.prob(t)
            ]))
        print("HAPAXES: %r" % self.freqdist.hapaxes())
        # freq of freqs:
        print("FreqDist: %r" % sorted(self.freqdist.values(), reverse=True))
        print("Slope: %r" % self.sgt._slope)
        print("Switch at: %r" % self.sgt._switch_at)
    
    def simulate(self, n=1000):
        keys = [k for k in self.probabilities]
        probs = [self.probabilities[k] for k in keys]
        
        # set up
        itercount = 0  # stopping safety valve
        transcript = []
        complete = False    # have we seen everything?
        seen = Counter({k: 0 for k in self.tokens})  # tokens we've seen
        while not complete:
            for char in np.random.choice(keys, n, replace=True, p=probs)[0:n]:
                transcript.append(char)
                seen[char] += 1
                complete = all(v > 0 for v in seen.values())
                
                if complete:
                    return len(transcript)
                
                if itercount >= STOP:
                    raise StopIteration("Abort Abort!")
                itercount += 1
            
        raise StopIteration("Failed")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Does something.')
    parser.add_argument("filename", help='filename')
    parser.add_argument(
        '-n', "--replicates", dest='replicates', default=1000,
        help="number of replicates", action='store', type=int
    )
    parser.add_argument(
        "--dump", dest='dump', help="dump", action='store_true', default=False
    )
    parser.add_argument(
        "--debug", dest='debug', help="debug", action='store_true', default=False
    )
    args = parser.parse_args()
    
    data = FileReader(args.filename)
    
    DEBUG = args.debug

    if args.dump:
        Simulator(data).dump()
        quit()

    for sim in range(1, args.replicates + 1):
        sys.stdout.write("%s\t%d\t%d\n" % (data.language, sim, Simulator(data).simulate()))
        sys.stdout.flush()
