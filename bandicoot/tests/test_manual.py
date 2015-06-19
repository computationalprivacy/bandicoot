"""
Test manual user files, made by real humans, with all metrics handcrafted.
"""

import bandicoot as bc
import unittest
from testing_tools import parse_dict, metric_suite
import os


class TestManual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestManual._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestManual._dir_changed = True

        self.user_A = bc.io.read_csv("A", "samples/manual", "samples/towers.csv", describe=False, network=False)
        self.user_B = bc.io.read_csv("B", "samples/manual", "samples/towers.csv", describe=False, network=False)
        self.user_A_orange = bc.io.read_orange("A_orange", "samples/manual", describe=False, network=False)

    def test_A_metrics(self):
        self.assertTrue(*metric_suite(self.user_A, parse_dict("samples/manual/A.json"), groupby=None, decimal=4))

    def test_B_metrics(self):
        self.assertTrue(*metric_suite(self.user_B, parse_dict("samples/manual/B.json"), groupby=None, decimal=3))

    def test_A_orange_metrics(self):
        self.assertTrue(*metric_suite(self.user_A_orange, parse_dict("samples/manual/A.json"), groupby=None, decimal=4))