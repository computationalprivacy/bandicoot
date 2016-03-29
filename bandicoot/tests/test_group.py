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
Test for the bandicoot.helper.group module.
"""

import bandicoot as bc
from bandicoot.core import Record, Position
import unittest
import datetime
from bandicoot.tests.generate_user import random_burst
from bandicoot.helper.group import group_records
from bandicoot.helper.maths import std, mean, SummaryStats
from datetime import timedelta
import numpy as np
import os


class TestGroup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestGroup._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestGroup._dir_changed = True

        self.maxDiff = None

        self.user = bc.io.read_orange("u_test", "samples", describe=False)
        self.random_int_list = np.random.randint(1, 1000, size=9001)

        self.sum_stats_list = [SummaryStats(np.random.rand(), np.random.rand(),
                               np.random.rand(), np.random.rand(), np.random.rand(), np.random.rand(), np.random.rand(), []) for _ in range(9001)]

    def test_statistics(self):
        self.assertDictEqual(bc.helper.group.statistics(self.random_int_list, summary='default'), {
            'mean': mean(self.random_int_list),
            'std': std(self.random_int_list),
        })

        def mean_std(key):
            return {
                'mean': mean([getattr(s, key) for s in self.sum_stats_list]),
                'std': std([getattr(s, key) for s in self.sum_stats_list]),
            }

        self.assertDictEqual(bc.helper.group.statistics(self.sum_stats_list, summary='extended'), {
            'kurtosis': mean_std('kurtosis'),
            'mean': mean_std('mean'),
            'median': mean_std('median'),
            'skewness': mean_std('skewness'),
            'std': mean_std('std'),
            'min': mean_std('min'),
            'max': mean_std('max')
        })

        self.assertEqual(list(bc.helper.group.statistics([]).values()), [None] * 2)

    def test_statistics_bad_aggregated(self):
        def run_bad_aggregated():
            try:
                bc.helper.group.statistics("bad_aggregated")
            except (TypeError, ValueError):
                return True
            return False
        self.assertTrue(run_bad_aggregated())

    def test_weekly_group(self):
        records = [
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 24), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 9, 4), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 9, 11), 1, Position())
        ]
        user = bc.User()
        user.records = records

        grouping = bc.helper.group.group_records(user.records, groupby='week')
        groups = [[r for r in l] for l in grouping]
        self.assertEqual(groups, [[records[0]], [records[1]], [records[2]]])

    def test_weekday_filter(self):
        records = [
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 22), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 31), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 10, 18), 1, Position())
        ]
        user = bc.User()
        user.records = records
        filtered_records = bc.helper.group.filter_user(user, part_of_week='weekday')
        self.assertEqual(filtered_records, [records[0]])

    def test_weekend_filter(self):
        records = [
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 22), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 31), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 10, 18), 1, Position())
        ]
        user = bc.User()
        user.records = records
        filtered_records = bc.helper.group.filter_user(user, part_of_week='weekend')
        self.assertEqual(filtered_records, [records[1], records[2]])

    def test_daily_filter(self):
        records = [
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 22, 10, 00), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 23, 10, 00), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 9, 7, 11, 00), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 10, 18, 2, 00), 1, Position())
        ]
        user = bc.User()
        user.records = records

        filtered_records = bc.helper.group.filter_user(user, part_of_day='night')
        self.assertEqual(filtered_records, [records[3]])

        filtered_records = bc.helper.group.filter_user(user, part_of_day='day')
        self.assertEqual(filtered_records, [records[0], records[1], records[2]])

    def test_none_group(self):
        records = [
            Record("call", "in", "1", datetime.datetime(2014, 9, 4), 1, Position()),
            Record("call", "in", "1", datetime.datetime(2014, 9, 5), 1, Position()),
            Record("call", "in", "1", datetime.datetime(2014, 9, 11), 1, Position()),
            Record("call", "in", "1", datetime.datetime(2014, 9, 12), 1, Position())
        ]

        grouping = bc.helper.group.group_records(records, groupby=None)
        self.assertEqual(records, list(next(grouping)))
        with self.assertRaises(StopIteration):
            next(grouping)


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.user = bc.User()
        self.user.records = random_burst(100, delta=timedelta(days=2))

    def _group_set(self, method, interaction):
        filtered_records = bc.helper.group.filter_user(self.user, interaction=interaction)
        chunks = group_records(filtered_records, groupby=method)

        new_records = set(r for c in chunks for r in c)
        return new_records

    def test_weekly(self):
        old_records = set(self.user.records)
        new_records = self._group_set('week', None)
        self.assertSetEqual(new_records, old_records)

        new_records = self._group_set('week', 'call')
        self.assertSetEqual(new_records, {r for r in old_records
                                          if r.interaction == 'call'})


class MissingTests(unittest.TestCase):
    def setUp(self):
        self.user = bc.read_csv('user_ignored', 'samples')

    def test_amount(self):
        result = {
            'all': 4,
            'interaction': 2,
            'direction': 2,
            'correspondent_id': 0,
            'datetime': 0,
            'call_duration': 1,
            'location': 0
        }
        self.assertDictEqual(self.user.ignored_records, result)

    def test_total_records(self):
        self.assertEqual(len(self.user.records), 1)
