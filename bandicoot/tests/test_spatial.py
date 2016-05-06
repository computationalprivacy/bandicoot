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

from __future__ import division

import unittest
import os

import bandicoot as bc
import numpy as np


class TestChurn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestChurn._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestChurn._dir_changed = True

        self.user = bc.io.read_csv("churn_user", "samples", describe=False, warnings=False)

    def test_churn(self):
        distribution = bc.spatial.churn_rate(self.user, summary=None)

        v1 = [1 / 3, 1 / 3, 1 / 3, 0]
        v2 = v1
        v3 = [1 / 4, 3 / 4, 0, 0]
        v4 = [0, 0, 1 / 2, 1 / 2]

        cos_1 = 1 - np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_2 = 1 - np.dot(v2, v3) / (np.linalg.norm(v2) * np.linalg.norm(v3))
        cos_3 = 1 - np.dot(v3, v4) / (np.linalg.norm(v3) * np.linalg.norm(v4))

        np.testing.assert_almost_equal(distribution, [cos_1, cos_2, cos_3])

        churn_rate = bc.spatial.churn_rate(self.user)
        np.testing.assert_almost_equal(churn_rate['mean'], np.mean([cos_1, cos_2, cos_3]))
        np.testing.assert_almost_equal(churn_rate['std'], np.std([cos_1, cos_2, cos_3]))
