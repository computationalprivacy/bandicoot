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
Test special non-core functionality such as the generation of punchcards.
"""

import bandicoot as bc
from bandicoot.weekmatrix import create_weekmatrices, to_csv
from .testing_tools import file_equality

import tempfile
import unittest
import os


class TestSpecial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestSpecial._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestSpecial._dir_changed = True

        self.user_X = bc.io.read_csv(
            "X", "samples/special", "samples/special/antennas.csv", describe=False, warnings=False)
        self.user_Y = bc.io.read_csv(
            "Y", "samples/special", describe=False, warnings=False)

    def assertAlmostEqualLists(self, list_a, list_b, places=5):
        self.assertTrue(len(list_a) == len(list_b))
        for i in range(len(list_a)):
            self.assertAlmostEqual(list_a[i], list_b[i])

    def test_X_matrices(self):
        self.X_weekmatrices = create_weekmatrices(
            self.user_X, split_interval=60)
        self.assertAlmostEqualLists(self.X_weekmatrices, bc.weekmatrix.read_csv(
            "samples/special/weekmatrix_X_60min_interval.csv"))

    def test_Y_matrices(self):
        self.Y_weekmatrices = create_weekmatrices(
            self.user_Y, split_interval=5)
        self.assertAlmostEqualLists(self.Y_weekmatrices, bc.weekmatrix.read_csv(
            "samples/special/weekmatrix_Y_5min_interval.csv"))

    def test_X_csv(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        print(tmp_file.name)

        X_weekmatrices = create_weekmatrices(self.user_X, split_interval=60)
        to_csv(X_weekmatrices, tmp_file.name)
        self.assertTrue(file_equality(tmp_file.name,
                        "samples/special/weekmatrix_X_60min_interval.csv"))

    def test_Y_csv(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        print(tmp_file.name)

        Y_weekmatrices = create_weekmatrices(self.user_Y, split_interval=5)
        to_csv(Y_weekmatrices, tmp_file.name)
        self.assertTrue(file_equality(tmp_file.name,
                        "samples/special/weekmatrix_Y_5min_interval.csv"))
