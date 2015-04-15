"""
Tests for bandicoot.core (User, Position, and Record classes)
"""

import bandicoot as bc
import unittest
import datetime
from testing_tools import parse_dict, metric_suite
import os


class TestSampleUser(unittest.TestCase):
    
    def setUp(self):
        self.sample_user    = bc.tests.generate_user.sample_user()

    def test_sample_user(self):
        self.assertTrue(*metric_suite(self.sample_user, parse_dict("samples/sample_user_all_metrics.json"), groupby=None, summary='extended', decimal=4))