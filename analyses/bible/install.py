#!/usr/bin/env python3
# coding=utf-8

import os
import sys
from shutil import copyfile
sys.path.append('../../bin')
from tools import get_table

from lib import BIBLE_DIR, SOURCE_DIR

if __name__ == '__main__':
    for row in get_table('bibles.txt'):
        if row.Language.startswith("#"):
            continue

        dst = os.path.join("bibles", row.Bible)
        src = os.path.join(SOURCE_DIR, row.Bible)
        copyfile(src, dst)
        print(src, '->', dst)
