#!/usr/bin/env python3
# coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2018 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
import subprocess
from random import shuffle

DATADIR = '../../data/jipa'
RESULTSDIR = 'results'

if __name__ == '__main__':
    filelist = [f for f in os.listdir(DATADIR) if f.endswith('.txt')]
    shuffle(filelist)

    for filename in filelist:
        base = os.path.splitext(filename)[0]
        log = "%s.dat" % os.path.join(RESULTSDIR, base)
        err = "%s.err" % os.path.join(RESULTSDIR, base)
        if not os.path.isfile(log):
            print("Generating: %s" % filename, flush=True)
            proc = subprocess.Popen(
                ['python', 'simulate.py', '-n', '1000', os.path.join(DATADIR, filename)],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            with open(log, 'w') as lf, open(err, 'w') as ef:
                for out in proc.communicate():
                    out = out.decode('utf8')
                    print("> %s" % out, flush=True)
                    if out.startswith(os.path.splitext(filename)[0]):
                        lf.write(out)
                    elif 'Warning' in out:
                        ef.write(out)
                    elif len(out) == 0:
                        continue
                    else:
                        raise ValueError("??")


