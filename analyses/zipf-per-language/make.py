#!/usr/bin/env python3
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2017 Simon J. Greenhill'
__license__ = 'New-style BSD'

import os

from fit import getfit, plot

DATADIR = '../../data/jipa'

if __name__ == '__main__':
    datafiles = [f for f in os.listdir(DATADIR) if f.endswith('.txt')]
    print("\t".join([
        'Language',
        'Alpha',
        'Sigma',
        'Xmin',
        'vsExp.R',
        'vsExp.P',
        'vsLN.R',
        'vsLN.P',
        'vsTPL.R',
        'vsTPL.P',
    ]))
    
    for df in datafiles:
        output = os.path.basename(df).replace('.txt', '.log')
        fit = getfit(os.path.join(DATADIR, df))
        plot(fit['fit'], '%s.pdf' % fit['f'].language)
        out = [
            fit['f'].language,
            '%0.3f' % fit['alpha'],
            '%0.3f' % fit['sigma'],
            '%d' % fit['xmin'],
            '%0.3f' % fit['vs_exponential'][0],
            '%0.3f' % fit['vs_exponential'][1],
            '%0.3f' % fit['vs_lognormal'][0],
            '%0.3f' % fit['vs_lognormal'][1],
            '%0.3f' % fit['vs_truncated'][0],
            '%0.3f' % fit['vs_truncated'][1],
        ]
        print("\t".join(out))
        del(fit)