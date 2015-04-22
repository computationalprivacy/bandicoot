"""
Tests for the sample user
"""

import bandicoot as bc
import unittest
from testing_tools import parse_dict


class TestSampleUser(unittest.TestCase):
    def setUp(self):
        self.sample_user = bc.tests.generate_user.sample_user()

    def test_sample_user(self):
        result = bc.utils.all(self.sample_user, groupby=None, summary='extended', flatten=True)
        self.assertDictEqual(result, parse_dict("samples/sample_user_all_metrics.json")['sample_user'])
