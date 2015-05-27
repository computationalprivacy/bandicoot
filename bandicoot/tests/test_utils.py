"""
Test the bandicoot.utils module, mostly using the numpy library.
"""

import bandicoot as bc
import unittest
from scipy import stats
import numpy as np
import os


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
        self.assertEqual(bc.helper.tools.skewness([]), None)
        self.assertAlmostEqual(bc.helper.tools.skewness([1, 2, 3, 4, 7]), stats.skew([1, 2, 3, 4, 7]))

    def test_kurtosis(self):
        self.assertEqual(bc.helper.tools.kurtosis([]), None)
        self.assertAlmostEqual(bc.helper.tools.kurtosis([1, 2, 3, 4, 5]), stats.kurtosis([1, 2, 3, 4, 5], fisher=False))
        self.assertAlmostEqual(bc.helper.tools.kurtosis([1, 6, 6, 6, 9, 17]), stats.kurtosis([1, 6, 6, 6, 9, 17], fisher=False))

        self.assertAlmostEqual(bc.helper.tools.kurtosis(self.list_1), stats.kurtosis(self.list_1, fisher=False))
        self.assertAlmostEqual(bc.helper.tools.kurtosis(self.list_2), stats.kurtosis(self.list_2, fisher=False))

    def test_mean(self):
        self.assertEqual(bc.helper.tools.mean([]), None)
        self.assertAlmostEqual(bc.helper.tools.mean(self.list_1), np.average(self.list_1))
        self.assertAlmostEqual(bc.helper.tools.mean(self.list_2), np.average(self.list_2))

    def test_std(self):
        self.assertEqual(bc.helper.tools.std([]), None)
        self.assertAlmostEqual(bc.helper.tools.std(self.list_1), np.std(self.list_1))
        self.assertAlmostEqual(bc.helper.tools.std(self.list_2), np.std(self.list_2))

    def test_median(self):
        self.assertEqual(bc.helper.tools.median([]), None)
        self.assertEqual(bc.helper.tools.median(self.list_1), np.median(self.list_1))
        self.assertEqual(bc.helper.tools.median(self.list_2), np.median(self.list_2))

    def test_entropy(self):
        self.assertEqual(bc.helper.tools.entropy([]), None)
        self.assertAlmostEqual(bc.helper.tools.entropy(self.list_2), stats.entropy(self.list_2))

    def test_great_circle_distance(self):
        pt1 = [-1, -1]
        pt2 = [1, 1]
        pt3 = [0, 0]
        pt4 = [100, -100]
        self.assertEqual(bc.helper.tools.great_circle_distance(pt1, pt2), 0)
        self.assertEqual(bc.helper.tools.great_circle_distance(pt1, pt3), 0)
        self.assertEqual(bc.helper.tools.great_circle_distance(pt1, pt4), 20015.086796020572)
        self.assertEqual(bc.helper.tools.great_circle_distance(pt2, pt3), 0)
        self.assertEqual(bc.helper.tools.great_circle_distance(pt2, pt4), 20015.086796020572)
        self.assertEqual(bc.helper.tools.great_circle_distance(pt3, pt4), 20015.086796020572)

    def test_summary_stats(self):
        self.assertEqual(bc.helper.tools.summary_stats([1, 5, 2]),
            bc.helper.tools.SummaryStats(mean=2.6666666666666665, std=1.699673171197595, min=1.0, max=5.0, median=2.0, skewness=0.5280049792181879, kurtosis=1.4999999999999998, distribution=[1, 2, 5]))
        self.assertEqual(bc.helper.tools.summary_stats([1, 2, 3]),
            bc.helper.tools.SummaryStats(mean=2.0, std=0.816496580927726, min=1.0, max=3.0, median=2.0, skewness=0.0, kurtosis=1.5, distribution=[1, 2, 3]))
        self.assertEqual(bc.helper.tools.summary_stats([]),
            bc.helper.tools.SummaryStats(mean=0., std=0., min=0., max=0., median=0., skewness=0., kurtosis=0., distribution=[]))

    def test_all(self):
        pass
