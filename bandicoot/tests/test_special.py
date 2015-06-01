"""
Test special non-core functionality such as the generation of punchcards.
"""

import bandicoot as bc
import unittest
from testing_tools import parse_dict, metric_suite
import os


class TestSpecial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestSpecial._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestSpecial._dir_changed = True

        self.user_X = bc.io.read_csv(
            "X", "samples/special", "samples/special/antennas.csv", describe=False, warnings=False)
        self.user_Y = bc.io.read_csv(
            "Y", "samples/special", describe=False, warnings=False)

    def assertAlmostEqualLists(self, list_a, list_b, places=5):
        self.assertTrue(len(list_a) == len(list_b))
        for i in range(len(list_a)):
            self.assertAlmostEqual(list_a[i], list_b[i])

    def test_X_punchcard(self):
        self.X_punchcards = bc.special.punchcard.create_punchcards(
            self.user_X, split_interval=60)
        self.assertAlmostEqualLists(self.X_punchcards, bc.special.punchcard.read_csv(
            "samples/special/punchcard_X_60min_interval.csv"))

    def test_Y_punchcard(self):
        self.Y_punchcards = bc.special.punchcard.create_punchcards(
            self.user_Y, split_interval=5)
        self.assertAlmostEqualLists(self.Y_punchcards, bc.special.punchcard.read_csv(
            "samples/special/punchcard_Y_5min_interval.csv"))
