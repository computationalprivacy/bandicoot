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

import bandicoot as bc
import unittest
from .testing_tools import file_equality
import tempfile
import os
from collections import OrderedDict as OD


class TestExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestExport._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestExport._dir_changed = True

    def test_different_keys(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        dict1 = {"x": 1, "y": 2, "z": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        try:
            bc.io.to_csv([dict1, dict2], tmp_file.name)
            self.assertTrue(file_equality(tmp_file.name,
                            "samples/to_csv_different_keys.csv"))
        finally:
            tmp_file.close()
            os.unlink(tmp_file.name)

    def test_same_keys(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        dict1 = {"a": 1, "b": 2, "c": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        try:
            bc.io.to_csv([dict1, dict2], tmp_file.name)
            self.assertTrue(file_equality(tmp_file.name,
                            "samples/to_csv_same_keys.csv"))
        finally:
            tmp_file.close()
            os.unlink(tmp_file.name)

    def test_different_json(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        dict1 = {"name": "dict1", "x": 1, "y": 2, "z": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"name": "dict2", "a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        try:
            bc.io.to_json([dict1, dict2], tmp_file.name)
            self.assertTrue(file_equality(tmp_file.name,
                            "samples/to_json_different_keys.json"))
        finally:
            tmp_file.close()
            os.unlink(tmp_file.name)

    def test_same_json(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        dict1 = {"name": "dict1", "a": 1, "b": 2, "c": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"name": "dict2", "a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        try:
            bc.io.to_json([dict1, dict2], tmp_file.name)
            self.assertTrue(file_equality(tmp_file.name,
                            "samples/to_json_same_keys.json"))
        finally:
            tmp_file.close()
            os.unlink(tmp_file.name)
