#!/usr/bin/env python3
# coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2018 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os
from random import sample

if __name__ == '__main__':
    filelist = [
        os.path.join('plots', f) for f in os.listdir('plots') if f.endswith('.pdf')
    ]
    filelist = sorted(sample(filelist, 4))
    print(filelist)

    args = []
    for f in filelist:
        args.append(
            "-label '%s' '%s'" % (
                os.path.split(os.path.splitext(f)[0])[1],
                f
            )
        )
    print("""
    # requires ImageMagick
    montage %s -density 300 -geometry 1200x1200 -tile 2x2 random.pdf
    """ % " ".join(args))


    # print("""
    # # requires ImageMagick
    # montage %s %s -density 300 -geometry 1200x1200 -tile 2x3 random.pdf
    # """ % (
    #     " ".join([ for f in filelist]),
    #     " ".join(['"%s"' % f for f in filelist])
    # ))
    # # gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=random.pdf %s

