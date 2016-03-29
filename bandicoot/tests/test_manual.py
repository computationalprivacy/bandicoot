# The MIT License (MIT)
#
# Copyright (c) 2015-2016 Massachusetts Institute of Technology.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Test manual user files, made by real humans, with all metrics handcrafted.
"""

import bandicoot as bc
import unittest
from .testing_tools import parse_dict, metric_suite
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

        self.user_A = bc.io.read_csv("A", "samples/manual", "samples/towers.csv", recharges_path="samples/manual/recharges", describe=False, network=False)
        self.user_B = bc.io.read_csv("B", "samples/manual", "samples/towers.csv", describe=False, network=False)
        self.user_A_orange = bc.io.read_orange("A_orange", "samples/manual", recharges_path="samples/manual/recharges", describe=False, network=False)

    def test_A_metrics(self):
        self.assertTrue(*metric_suite(self.user_A, parse_dict("samples/manual/A.json"), groupby=None, decimal=4))

    def test_B_metrics(self):
        self.assertTrue(*metric_suite(self.user_B, parse_dict("samples/manual/B.json"), groupby=None, decimal=3))

    def test_A_orange_metrics(self):
        self.assertTrue(*metric_suite(self.user_A_orange, parse_dict("samples/manual/A.json"), groupby=None, decimal=4))
