"""
Test for the bandicoot.helper.group module.
"""

import bandicoot as bc
from bandicoot.core import Record, Position
import unittest
import datetime
from bandicoot.tests.generate_user import random_burst
from bandicoot.helper.group import group_records
from bandicoot.helper.tools import std, mean, minimum, maximum
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

        self.user = bc.io.read_orange("samples/u_test.csv", describe=False)
        self.random_int_list = np.random.randint(1, 1000, size=9001)

        self.sum_stats_list = [bc.helper.tools.SummaryStats(np.random.rand(), np.random.rand(),
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

        self.assertEqual(bc.helper.group.statistics([]).values(), [None] * 2)

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

        grouping = bc.helper.group.group_records(user, groupby='week')
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[0].datetime)
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[1].datetime)
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[2].datetime)

    def test_weekday_group(self):
        records = [
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 25), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 9, 4), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 9, 11), 1, Position())
        ]
        user = bc.User()
        user.records = records

        grouping = bc.helper.group.group_records(user, groupby='week', part_of_week='weekday')
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[0].datetime)
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[1].datetime)
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[2].datetime)

    def test_weekend_group(self):
        records = [
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 23), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 8, 31), 1, Position()),
            Record("test_itr", "in", "1", datetime.datetime(2014, 10, 18), 1, Position())
        ]
        user = bc.User()
        user.records = records

        grouping = bc.helper.group.group_records(user, groupby='week', part_of_week='weekend')
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[0].datetime)
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[1].datetime)
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[2].datetime)

    def test_none_group(self):
        records = [
            Record("call", "in", "1", datetime.datetime(2014, 9, 5), 1, Position()),
            Record("call", "in", "1", datetime.datetime(2014, 9, 4), 1, Position()),
            Record("call", "in", "1", datetime.datetime(2014, 9, 11), 1, Position()),
            Record("call", "in", "1", datetime.datetime(2014, 9, 12), 1, Position())
        ]
        user = bc.User()
        user.records = records

        grouping = bc.helper.group.group_records(user, groupby=None)
        record = grouping.next()
        self.assertTrue(record.next().datetime, records[0].datetime)
        self.assertTrue(record.next().datetime, records[1].datetime)
        self.assertTrue(record.next().datetime, records[2].datetime)
        self.assertTrue(record.next().datetime, records[3].datetime)
        self.assertRaises(StopIteration, record.next)
        self.assertRaises(StopIteration, grouping.next)


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.user = bc.User()
        self.user.records = random_burst(100, delta=timedelta(days=2))

    def _group_set(self, method, interaction):
        chunks = group_records(self.user, groupby='method',
                               interaction=interaction)
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
        }
        self.assertDictEqual(self.user.ignored_records, result)

    def test_total_records(self):
        self.assertEqual(len(self.user.records), 1)
