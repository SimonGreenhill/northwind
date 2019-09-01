#Counter!/usr/bin/env python3
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2017 Simon J. Greenhill'
__license__ = 'New-style BSD'

import io
import sys
sys.path.append('../../bin')
from tools import FileReader

from contextlib import redirect_stderr
from collections import Counter

import numpy
import pylab  # matplotlib
import powerlaw

numpy.seterr(divide='ignore', invalid='ignore')

def is_sig(p):
    if p <= 0.05:
        return '*'
    return ''

def getfit(filename, xmin=None):
    f = FileReader(filename)
    data = Counter(f.transcript)
    data = [int(v) for v in sorted(data.values(), reverse=True)]
    fit = powerlaw.Fit(
        data=data,
        # we have discrete data..
        discrete=True,
        # calculating the fit exactly with slow numerical method
        estimate_discrete=False,
        # set xmin to 1 as that's Zipf and we need all the data (see: Clauset et al)
        xmin=xmin if not xmin else xmin,
        # be quiet
        verbose=False
    )

    shutup = io.StringIO()
    with redirect_stderr(shutup):
        return {
            'fit': fit,
            'alpha': fit.alpha,
            'sigma': fit.sigma,
            'xmin': fit.xmin,
            'data': data,
            'f': f,
            'vs_exponential': fit.distribution_compare(
                'power_law', 'exponential',
                normalized_ratio=True
            ),
            'vs_lognormal': fit.distribution_compare(
                'power_law', 'lognormal',
                normalized_ratio=True
            ),
            'vs_truncated': fit.distribution_compare(
                'power_law', 'truncated_power_law',
                nested=True,  # for some reason this doesn't shut up the error?
                normalized_ratio=True,
            ),
            'e_vs_tpl':fit.distribution_compare(
                'exponential', 'truncated_power_law',
                normalized_ratio=True,
            )

        }

def plot(fit, filename):
    pylab.figure()
    fit.distribution_compare('power_law', 'lognormal')
    fig = fit.plot_ccdf(linewidth=1, marker='o', label='Empirical Data')
    fit.power_law.plot_ccdf(ax=fig, color='r', linestyle=':', label='Power law fit')
    fit.truncated_power_law.plot_ccdf(ax=fig, color='g', linestyle=':', label='Truncated Power law fit')
    fit.exponential.plot_ccdf(ax=fig, color='black', linestyle=':', label='Exponential fit')
    fig.set_ylabel(u"p(X≥x)")
    fig.set_xlabel("Token Frequency")
    handles, labels = fig.get_legend_handles_labels()
    fig.legend(handles, labels, loc=3)
    pylab.savefig(filename)
    pylab.close()
    return



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Does something.')
    parser.add_argument("filename", help='filename')
    args = parser.parse_args()
    
    fit = getfit(args.filename)
    plot(fit['fit'], 'plots/%s.pdf' % fit['f'].language)
    
    print("alpha           = %0.3f" % fit['alpha'])   # alpha ~= 1 is Zipf
    print("sigma           = %0.3f" % fit['sigma'])
    print("xmin            = %0.3f" % fit['xmin'])
    print("n               = %0.3f" % len(fit['data']))
    print('positive number if first distribution is more likely')
    print("powerlaw vs exponential  = %0.3f (p=%0.3f)" % fit['vs_exponential'])
    print("powerlaw vs lognormal    = %0.3f (p=%0.3f)" % fit['vs_lognormal'])
    print("powerlaw vs truncated pl = %0.3f (p=%0.3f)" % fit['vs_truncated'])
    print("exponential vs truncated pl = %0.3f (p=%0.3f)" % fit['e_vs_tpl'])
