"""
Test the import of CSV files.
"""

import bandicoot as bc
from bandicoot.core import Record, Position
import unittest
from StringIO import StringIO
import sys
import datetime
import csv
import os

class TestParsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestParsers._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestParsers._dir_changed = True

        self.stdin = StringIO("""1;22;770000000;770000005;2013-12-16 07:30:30;0;42.3987;-71.5750
            1;11;770000000;770000008;2013-12-16 08:30:30;126;42.1534;-70.7084
            2;22;770000000;770000007;2013-12-16 17:30:30;0;42.6590;-71.1216""")
        sys.stdin = self.stdin

    def tearDown(self):
        sys.stdin = sys.__stdin__

    def test_read_orange(self):
        user = bc.io.read_orange("samples/u_test.csv", describe=False)
        self.assertEqual(len(user.records), 500)

    def test_read_orange_stdin(self):
        user = bc.io.read_orange(describe=False)
        self.assertEqual(user.records[0],
                         Record(interaction='text',
                                direction='out',
                                correspondent_id='770000005',
                                datetime=datetime.datetime(2013, 12, 16, 7, 30, 30),
                                call_duration=0.0,
                                position=Position(1, (42.3987, -71.575))))

    def test_read_orange_from_reader(self):
        with open("samples/u_test.csv") as f:
            r = csv.reader(f, delimiter=';')
            user = bc.io.read_orange(r, describe=False)
        self.assertEqual(len(user.records), 500)

    def test_read_csv(self):
        user = bc.read_csv("u_test2", "samples", describe=False)
        self.assertEqual(len(user.records), 500)

    def test_read_csv_antenna_id_no_places(self):
        user = bc.read_csv("u_test_antennas", "samples", describe=False)
        self.assertEqual(user.records[1],
                         Record(interaction='call',
                                direction='in',
                                correspondent_id='770000001',
                                datetime=datetime.datetime(2013, 12, 16, 5, 39, 30),
                                call_duration=0,
                                position=Position('13084', None)))

        result = {'allweek': {'allday': None}}
        self.assertEqual(bc.spatial.radius_of_gyration(user, groupby=None), result)

    def test_read_csv_antenna_id(self):
        user = bc.read_csv("u_test_antennas", "samples", antennas_path="samples/towers.csv", describe=False)
        self.assertEqual(user.records[1],
                         Record(interaction='call',
                                direction='in',
                                correspondent_id='770000001',
                                datetime=datetime.datetime(2013, 12, 16, 5, 39, 30),
                                call_duration=0,
                                position=Position('13084', None)))

        radius = bc.spatial.radius_of_gyration(user, groupby=None)['allweek']['allday']
        self.assertGreater(radius, 0)

    def test_read_csv_no_position(self):
        user = bc.read_csv("u_test_no_position", "samples", describe=False)
        self.assertEqual(user.records[1],
                         Record(interaction='call',
                                direction='in',
                                correspondent_id='770000001',
                                datetime=datetime.datetime(2013, 12, 16, 5, 39, 30),
                                call_duration=0,
                                position=Position()))

    def test_read_csv_attributes(self):
        user = bc.read_csv("u_test2", "samples", attributes_path="samples/attributes", describe=False)
        self.assertEqual(user.attributes, {
            'gender': 'male',
            'age': '42',
            'is_subscriber': 'True',
            'individual_id': '7atr8f53fg41'
        })
