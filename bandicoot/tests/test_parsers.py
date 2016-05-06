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
Test the import of CSV files.
"""

import bandicoot as bc
from bandicoot.core import Record, Position
import unittest
import datetime
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

    def test_read_orange(self):
        user = bc.io.read_orange("u_test", "samples", describe=False)
        self.assertEqual(len(user.records), 500)

    def test_read_csv(self):
        user = bc.read_csv("u_test2", "samples", describe=False)
        self.assertEqual(len(user.records), 500)

    def test_read_csv_with_recharges(self):
        user = bc.read_csv("A", "samples/manual", describe=False,
                           recharges_path="samples/manual/recharges")
        self.assertEqual(len(user.recharges), 5)

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

    def test_read_duration_format(self):
        raw = {
            'antenna_id': '11201|11243',
            'call_duration': '873',
            'correspondent_id': 'A',
            'datetime': '2014-06-01 01:00:00',
            'direction': 'out',
            'interaction': 'call'
        }
        self.assertEqual(bc.io._parse_record(raw, duration_format='seconds').call_duration, 873)

        raw['call_duration'] = '00:14:33'
        self.assertEqual(bc.io._parse_record(raw, duration_format='%H:%M:%S').call_duration, 873)

        raw['call_duration'] = '1433'
        self.assertEqual(bc.io._parse_record(raw, duration_format='%M%S').call_duration, 873)

        raw['call_duration'] = ''
        self.assertEqual(bc.io._parse_record(raw, duration_format='seconds').call_duration, None)
