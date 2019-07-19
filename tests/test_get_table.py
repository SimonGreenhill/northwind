"""Test Slugify"""

import unittest
import sys
sys.path.append('../bin')
from tools import get_table

class TestGetTable(unittest.TestCase):
    def test(self):
        records = list(get_table('test_get_table.dat'))
        assert len(records) == 1
        assert records[0].ID == '1'
        assert records[0].Language == 'A'
        assert records[0].Word == 'B'
        assert records[0].Item == 'C'
        assert records[0].Cognacy == 'D'
        assert records[0].Loan == '0'
