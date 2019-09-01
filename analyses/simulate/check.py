#!/usr/bin/env python3
# coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2018 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
import codecs
import subprocess

from make import DATADIR, RESULTSDIR

if __name__ == '__main__':
    with codecs.open('check.log', 'w', 'utf8') as handle:
        for filename in sorted(os.listdir(DATADIR)):
            if not filename.endswith(".txt"):
                continue
                
            handle.write("\n")
            handle.write("-" * 76)
            handle.write("\n")
            handle.write("FILENAME: %s" % filename)
            handle.write("\n")
            cmd = [
                'python', 'simulate.py', '--dump',
                os.path.join(DATADIR, filename)
            ]
            proc = subprocess.Popen(cmd,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            for out in proc.communicate():
                handle.write(out.decode('utf8'))
            