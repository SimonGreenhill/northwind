#!/usr/bin/env python
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2017 Simon J. Greenhill'
__license__ = 'New-style BSD'

from fit import getfit, plot

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Does something.')
    parser.add_argument("filename", help='filename')
    parser.add_argument(
        '-v', "--verbose", dest='verbose',
        help="increases verbosity", action='store_true'
    )
    args = parser.parse_args()

    fit = getfit(args.filename)
    plot(fit['fit'], '%s.pdf' % fit['f'].language)
