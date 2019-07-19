import unittest
import sys
sys.path.append('../bin')
from tools import load_data

class TestLoadData(unittest.TestCase):
    def test(self):
        for f in load_data('.'):
            pass
