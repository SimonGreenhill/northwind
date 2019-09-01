#!/usr/bin/env python
# coding=utf-8
# pragma: no cover
import os
from collections import Counter

from tools import FileReader


def get_missing_flag(token):
    if token.is_missing and not token.known_missing:
        return "*"
    elif token.is_missing and token.known_missing:
        return "+"
    else:
        return ""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dumps debug data for a given file")
    parser.add_argument("filename", help="filename")
    parser.add_argument(
        "-q", "--quiet", dest="quiet", help="be quiet", action="store_true"
    )
    parser.add_argument(
        "-x", "--explode", dest="explode", help="drop into IPython", action="store_true"
    )
    args = parser.parse_args()

    assert os.path.isfile(args.filename), "missing %s" % args.filename

    f = FileReader(args.filename)

    print("Inventory:", f.inventory)
    print("Known Missings:", f.known_missings)
    print("Default Tokens:", f.default_tokens)
    print("")

    if args.explode:
        import IPython
        IPython.embed()
    
    mcount, kcount = Counter(), Counter()
    for i, token in enumerate(f.transcript, 1):
        if not args.quiet:
            print(
                "%d.\t%s\t%s\t%s"
                % (
                    i,
                    token.raw.ljust(35),
                    token.phoneme_type.ljust(10),
                    get_missing_flag(token),
                )
            )
        if token.is_missing and token.known_missing:
            kcount[token.raw] += 1
        elif token.is_missing and not token.known_missing:
            mcount[token.raw] += 1

    total = len(f.data["tokenised_transcript"])

    if not args.quiet or sum(mcount.values()) > 0:
        print("")
        print(
            "MISSING: %s (errors=%d/%d): missing=%r  expected=%r"
            % (args.filename, sum(mcount.values()), total, dict(mcount), dict(kcount))
        )

    if args.explode:
        import IPython
        IPython.embed()
