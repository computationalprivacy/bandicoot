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
Tests for bandicoot.core (User, Position, and Record classes)
"""

import bandicoot as bc
from .testing_tools import parse_dict

import unittest
import datetime
import sys
import os

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


class TestCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestCore._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestCore._dir_changed = True

        self.user = bc.io.read_orange("u_test", "samples", describe=False)

        self.user_nocturnal = bc.io.read_orange(
            "u_test", "samples", describe=False)
        self.user_nocturnal.night_start = datetime.time(7, 0)
        self.user_nocturnal.night_end = datetime.time(19, 0)

        self.maxDiff = None

    def test_recompute_home_place(self):
        old_home = self.user.home
        new_home = self.user.recompute_home()

        self.assertEqual(old_home, new_home)
        self.assertEqual(old_home, self.user.home)

    def test_set_home(self):
        towers = parse_dict("samples/towers.json")
        towers = {key: tuple(value) for (key, value) in towers.items()}
        new_home = bc.core.Position(antenna=towers["1"])
        self.user.set_home(new_home)
        self.assertEqual(self.user.home, new_home)

        new_home = bc.core.Position(location=(42.3555368, -71.099507))
        self.user.set_home((42.3555368, -71.099507))
        self.assertEqual(self.user.home, new_home)


class TestTowers(unittest.TestCase):
    def setUp(self):
        self.user = bc.io.read_csv(
            "A", "samples/manual/", "samples/towers.csv", describe=False)

    def testParse(self):
        towers = parse_dict("samples/towers.json")
        towers = {key: tuple(value) for (key, value) in towers.items()}

        self.assertDictEqual(self.user.antennas, towers)


class TestDescribe(unittest.TestCase):
    def setUp(self):
        self.empty_user = bc.User()
        self.sample_user = bc.tests.sample_user()

    def test_describe_empty(self):
        stdout_, stream = sys.stdout, StringIO()

        try:
            sys.stdout = stream
            self.empty_user.describe()
        finally:
            sys.stdout = stdout_

        rv = stream.getvalue().strip()
        baseline = """\x1b[32m[ ]\x1b[0m No records stored
\x1b[32m[ ]\x1b[0m No contacts
\x1b[32m[ ]\x1b[0m No attribute stored
\x1b[32m[ ]\x1b[0m No antenna stored
\x1b[32m[ ]\x1b[0m No recharges
\x1b[32m[ ]\x1b[0m No home
\x1b[32m[ ]\x1b[0m No texts
\x1b[32m[ ]\x1b[0m No calls
\x1b[32m[ ]\x1b[0m No network"""
        self.assertEqual(rv, baseline)

    def test_describe_sample(self):
        stdout_, stream = sys.stdout, StringIO()

        try:
            sys.stdout = stream
            self.sample_user.describe()
        finally:
            sys.stdout = stdout_

        rv = stream.getvalue().strip()
        baseline = """\x1b[32m[x]\x1b[0m 1482 records from 2012-01-01 00:14:24 to 2012-02-27 10:52:45
\x1b[32m[x]\x1b[0m 48 contacts
\x1b[32m[ ]\x1b[0m No attribute stored
\x1b[32m[x]\x1b[0m 7 antennas
\x1b[32m[ ]\x1b[0m No recharges
\x1b[32m[x]\x1b[0m Has home
\x1b[32m[x]\x1b[0m Has texts
\x1b[32m[x]\x1b[0m Has calls
\x1b[32m[x]\x1b[0m Has network"""
        self.assertEqual(rv, baseline)
