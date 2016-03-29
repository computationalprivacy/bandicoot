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

import unittest
import bandicoot as bc
from bandicoot.tests.generate_user import random_burst

from datetime import timedelta



class InterEventTests(unittest.TestCase):
    def setUp(self):
        self.user = bc.User()

    def test_empty_interevent(self):
        self.user.records = []
        interevent = bc.individual.interevent_time(self.user)
        self.assertEqual(list(interevent['allweek']['allday']['text'].values()), [None] * 2)

    def test_sequence_interevent(self):
        # 10 minutes burst
        _delta = timedelta(hours=2, minutes=13)
        self.user.records = random_burst(100, interaction='text',
                                         delta=_delta)
        interevent = bc.individual.interevent_time(self.user, groupby=None)
        self.assertEqual(interevent['allweek']['allday']['text']['mean'],
                         _delta.total_seconds())
        self.assertEqual(interevent['allweek']['allday']['text']['std'], 0)

        _delta = timedelta(hours=10, minutes=10)
        self.user.records = random_burst(100, interaction='text',
                                         delta=_delta)
        interevent = bc.individual.interevent_time(self.user, groupby=None)
        self.assertEqual(interevent['allweek']['allday']['text']['mean'],
                         _delta.total_seconds())
