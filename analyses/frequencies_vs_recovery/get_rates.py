#!/usr/bin/env python3
#coding=utf-8
import os
import sys
sys.path.append('../../bin')
import codecs
import statistics
import unicodedata
from collections import Counter, defaultdict

# Measure 1
# Phoneme X, rank R on (phoible or some other) top 100
# Ni = number of illustrations listing the phoneme in inventory
# Nt = number of illustrations attesting the phoneme in NWS text
# C = Nt/Ni (i.e. type capture rate)
# Measure correlation of R and C (e.g. by rank correlation)


# Measure 2
# Rank R as for Measure 1
# Rank P = rank in text (L) by token frequency
# Ni = number of illustrations listing the phoneme in inventory
# Nt = number of illustrations attesting the phoneme in NWS text
# Measure correlation of R and P


# The Phoible data is based on phonemes, so I think we should keep our analysis
# at the phonemic level as well, rather than the allophonic level. That means,
# given <n(n, n̪, ɲ, ŋ)>, if you have see [ɲ] five times and [ŋ] 3 times,
# what you've actually seen is /n/ eight times.


from tools import load_data, Token

CUTOFF = 250

FILENAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'top 250 sound segments.txt'
)

def read_phoible(filename=FILENAME, END=CUTOFF):
    with codecs.open(filename, 'r', 'utf8') as handle:
        for line in handle:
            line = unicodedata.normalize('NFC', line.strip())
            
            if len(line) == 0:
                continue
            if line == 'Notes:':  # pragma: no cover
                break

            idx, token = line.split(" ", 1)
            
            if ' = ' in token:
                token = token.split(" = ")[1]
            
            if '*' in token:
                continue
            
            idx = int(idx)
            if idx > END:
                break
            yield (idx, token)


def to_phoible(token, phoible):
    if token.raw in phoible:
        return token.raw
    elif token.token in phoible:
        return token.token
    # check allophones
    if token.allophones:
        for allo in token.allophones:
            if allo in phoible:
                return allo
    return None


phoible = {t: i for (i, t) in read_phoible()}
# Ni = number of illustrations listing the phoneme in inventory
Ni = Counter({p:0 for p in phoible})
# Nt = number of illustrations attesting the phoneme in NWS text
Nt = Counter({p: 0 for p in phoible})
# Rank P = rank in text (L) by token frequency
Ranks = Counter({p: 0 for p in phoible})

FirstObservs = defaultdict(list)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Does something.')
    parser.add_argument("filename", help='filename')
    args = parser.parse_args()
    
    nw_missing, nw_seen = Counter(), 0
    for f in load_data():
        # update Ni
        for token in f.tokens:
            if token.phoneme_type in ('tone', 'other', 'punctuation'):
                continue
            p = to_phoible(token, phoible)
            if p:
                nw_seen += 1
                Ni[p] += 1
                if token in f.transcript:
                    Nt[p] += 1
                    Ranks[p] += f.transcript.count(token)
                    first_obs = (f.transcript.index(token) / len(f.transcript)) * 100
                    FirstObservs[p].append(first_obs)
            else:
                nw_missing[str(token)] += 1
            
    freqs = {r[0]: i for (i, r) in enumerate(Ranks.most_common())}
    
    
    np = [t for t in Ni if Ni[t] == 0]
    print("Phonemes in Phoible never seen: %d / %d" % (len(np), len(phoible)))
    print("Phonemes in NWS never seen: %d / %d" % (len(nw_missing), nw_seen))
    
    with codecs.open(args.filename, 'w', 'utf8') as handle:
        handle.write("Phoneme\tRank\tNi\tNt\tC\tR\tAverageFirstObservationPercent\tFirstObservationSD\n")
        for p in Ni:
            try:
                C = (Nt[p] / Ni[p])
            except ZeroDivisionError:
                C = 0
            
            fo = FirstObservs.get(p, [100, ])  # set to 100 if None

            handle.write("\t".join([
                p,
                # Rank of P
                '%d' % phoible[p],
                # Ni = number of illustrations listing the phoneme in inventory
                '%d' % Ni[p],
                # Nt = number of illustrations attesting the phoneme in NWS text
                '%d' % Nt[p],
                # C = Nt/Ni (i.e. type capture rate)
                '%0.3f' % C,
                # Rank P = rank in text (L) by token frequency
                '%d' % freqs.get(p, 0),
                # Average First Observation Percent
                '%0.4f' % statistics.median(fo),
                '%0.4f' % statistics.stdev(fo) if len(fo) > 2 else '0.0'
            ]))
            handle.write("\n")
