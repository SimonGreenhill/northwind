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
    def __init__(self, tokens, frequencies, debug=DEBUG, stop=STOP):
        self.freqdist = frequencies
        self.tokens = tokens | set(self.freqdist)
        self.DEBUG = debug
        self.STOP = stop
        
        if len(self.freqdist) == 0:
            raise ValueError("No frequencies given!")
        
        while not self.freqdist.hapaxes():
            warnings.warn("no hapaxes present -- shifting distribution down")
            min_freq = min(self.freqdist.values()) - 1
            for k in self.freqdist:
                self.freqdist[k] -= min_freq

        
        if min(self.freqdist.values()) != 0:
            warnings.warn("no unseen present -- adding dummy category")
            self.tokens.add("<dummy>")

        self.sgt = SimpleGoodTuringProbDist(
            self.freqdist, bins=len(self.tokens)
        )
        self._get_probabilities()

    def _get_probabilities(self):
        self.probabilities = {}
        for t in self.tokens:
            self.probabilities[t] = self.sgt.prob(t)
        return self.probabilities

    def dump(self):  # pragma: no cover
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
                
                # if self.DEBUG:
                #     print(itercount, len(transcript))
                #
                if complete:
                    return len(transcript)
                
                if itercount >= self.STOP:
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
    
    freqdist = FreqDist(data.transcript)
    # set tokens to be all the observed tokens AND the ones on the inventory
    tokens = set(data.inventory) | set(freqdist)

    if args.dump:
        Simulator(tokens, freqdist, args.debug).dump()
        quit()

    for sim in range(1, args.replicates + 1):
        sys.stdout.write("%s\t%d\t%d\n" % (data.language, sim, Simulator(tokens, freqdist, debug=args.debug).simulate()))
        sys.stdout.flush()
