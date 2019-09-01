import os
import sys
import codecs
from collections import Counter, defaultdict

sys.path.append('../../bin')
from tools import get_cumulative_coverage as gcc_base


JIPA_DIR = "../../data/jipa"
BIBLE_DIR = "./bibles"
SOURCE_DIR = "/Users/simon/files/Data/paralleltext/bibles/corpus/"

# The paralleltext website seems to be down
# so use a local clone of https://github.com/cysouw/paralleltext/
# http://paralleltext.info/data/haw-x-bible/41/001/
# ~/files/Data/paralleltext/bibles/corpus/haw-x-bible.txt
def collect_bibles(datadir=SOURCE_DIR):
    bibles = defaultdict(list)
    for filename in os.listdir(datadir):
        iso = filename.split("-")[0]
        assert len(iso) == 3
        bibles[iso].append(filename)
    return bibles


def read_bible(biblefile):
    with codecs.open(biblefile, 'r', 'utf8') as handle:
        for line in handle:
            if line[0].startswith("#"):
                continue
            elif len(line.strip()):
                line = [_.strip() for _ in line.split("\t")]
                if len(line) == 1:  # pragma: no cover
                    yield(line, "")
                else:
                    yield(line[0], line[1])


def tally_bible(reader, biblefile, log=True):
    tally = Counter()
    for i, (pos, line) in enumerate(read_bible(biblefile), 1):
        tally.update(reader.toIPA(line))
        if log:  # pragma: no cover
            sys.stdout.write("\rReading %6d %10s" % (i, pos))
            sys.stdout.flush()
    # clean stdout and return
    sys.stdout.write('\r\n')
    sys.stdout.flush()
    return tally

