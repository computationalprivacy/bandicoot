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
Test the bandicoot.utils module, mostly using the numpy library.
"""

import bandicoot as bc
import unittest
from scipy import stats
import numpy as np
import os
import copy
from datetime import datetime


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestUtils._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestUtils._dir_changed = True

        self.user = bc.io.read_orange("u_test", "samples", describe=False)

        self.list_1 = np.random.randint(-1000, 1000, size=10000)
        self.list_2 = np.random.randint(1, 1000, size=9001)

    def test_flatten(self):
        d = {'alpha': 1, 'beta': {'a': 10, 'b': 42}}
        self.assertEqual(bc.utils.flatten(d), {
            'alpha': 1,
            'beta__a': 10,
            'beta__b': 42})
        self.assertEqual(bc.utils.flatten(d, separator='.'), {
            'alpha': 1,
            'beta.a': 10,
            'beta.b': 42})

    def test_skewness(self):
        self.assertEqual(bc.helper.maths.skewness([]), None)
        self.assertAlmostEqual(
            bc.helper.maths.skewness([1, 2, 3, 4, 7]), stats.skew([1, 2, 3, 4, 7]))

    def test_kurtosis(self):
        self.assertEqual(bc.helper.maths.kurtosis([]), None)
        self.assertAlmostEqual(bc.helper.maths.kurtosis(
            [1, 2, 3, 4, 5]), stats.kurtosis([1, 2, 3, 4, 5], fisher=False))
        self.assertAlmostEqual(bc.helper.maths.kurtosis(
            [1, 6, 6, 6, 9, 17]), stats.kurtosis([1, 6, 6, 6, 9, 17], fisher=False))

        self.assertAlmostEqual(bc.helper.maths.kurtosis(
            self.list_1), stats.kurtosis(self.list_1, fisher=False))
        self.assertAlmostEqual(bc.helper.maths.kurtosis(
            self.list_2), stats.kurtosis(self.list_2, fisher=False))

    def test_mean(self):
        self.assertEqual(bc.helper.maths.mean([]), None)
        self.assertAlmostEqual(
            bc.helper.maths.mean(self.list_1), np.average(self.list_1))
        self.assertAlmostEqual(
            bc.helper.maths.mean(self.list_2), np.average(self.list_2))

    def test_std(self):
        self.assertEqual(bc.helper.maths.std([]), None)
        self.assertAlmostEqual(
            bc.helper.maths.std(self.list_1), np.std(self.list_1))
        self.assertAlmostEqual(
            bc.helper.maths.std(self.list_2), np.std(self.list_2))

    def test_median(self):
        self.assertEqual(bc.helper.maths.median([]), None)
        self.assertEqual(
            bc.helper.maths.median(self.list_1), np.median(self.list_1))
        self.assertEqual(
            bc.helper.maths.median(self.list_2), np.median(self.list_2))

    def test_entropy(self):
        self.assertEqual(bc.helper.maths.entropy([]), None)
        self.assertAlmostEqual(
            bc.helper.maths.entropy(self.list_2), stats.entropy(self.list_2))

    def test_great_circle_distance(self):
        pt1 = [-1., -1.]
        pt2 = [1, 1]
        pt3 = [0., 0.]
        pt4 = [100, -100]
        self.assertEqual(bc.helper.maths.great_circle_distance(pt1, pt1), 0)
        self.assertEqual(bc.helper.maths.great_circle_distance(pt2, pt2), 0)
        self.assertAlmostEqual(
            bc.helper.maths.great_circle_distance(pt1, pt2), 314.4987625438879)
        self.assertAlmostEqual(
            bc.helper.maths.great_circle_distance(pt1, pt3), 157.2493812719439)
        self.assertAlmostEqual(
            bc.helper.maths.great_circle_distance(pt1, pt4), 9944.003359395136)
        self.assertAlmostEqual(
            bc.helper.maths.great_circle_distance(pt2, pt3), 157.2493812719439)
        self.assertAlmostEqual(
            bc.helper.maths.great_circle_distance(pt2, pt4), 9686.845683213172)
        self.assertAlmostEqual(
            bc.helper.maths.great_circle_distance(pt3, pt4), 9815.405117224152)

    def test_summary_stats(self):
        rv = bc.helper.maths.SummaryStats(
            mean=2.6666666666666665, std=1.699673171197595,
            min=1.0, max=5.0, median=2.0, skewness=0.5280049792181879,
            kurtosis=1.4999999999999998, distribution=[1, 2, 5])
        self.assertEqual(bc.helper.maths.summary_stats([1, 5, 2]), rv)

        rv = bc.helper.maths.SummaryStats(
            mean=2.0, std=0.816496580927726, min=1.0, max=3.0, median=2.0,
            skewness=0.0, kurtosis=1.5, distribution=[1, 2, 3])
        self.assertEqual(bc.helper.maths.summary_stats([1, 2, 3]), rv)

        rv = bc.helper.maths.SummaryStats(
            mean=None, std=None, min=None, max=None, median=None,
            skewness=None, kurtosis=None, distribution=[])
        self.assertEqual(bc.helper.maths.summary_stats([]), rv)

    def test_percent_overlap(self):
        raw = {
            'antenna_id': '11201|11243',
            'call_duration': '600', 'correspondent_id': 'A',
            'datetime': '2014-06-01 01:00:00',
            'direction': 'out', 'interaction': 'call'
        }
        record_A = bc.io._parse_record(raw)

        # previous overlap this by 2 min
        record_B = copy.deepcopy(record_A)
        record_B.datetime = datetime.strptime(
            'Jun 1 2014  1:08AM', '%b %d %Y %I:%M%p')

        # no overlap
        record_C = copy.deepcopy(record_A)
        record_C.datetime = datetime.strptime(
            'Jun 1 2014  1:19AM', '%b %d %Y %I:%M%p')

        # previous overlap this by 6 min
        record_D = copy.deepcopy(record_A)
        record_D.datetime = datetime.strptime(
            'Jun 1 2014  1:23AM', '%b %d %Y %I:%M%p')

        records = [record_A, record_B, record_C, record_D]
        self.assertAlmostEqual(
            bc.helper.tools.percent_overlapping_calls(records, 0), 0.5)
        self.assertAlmostEqual(
            bc.helper.tools.percent_overlapping_calls(records, 300), 0.25)
