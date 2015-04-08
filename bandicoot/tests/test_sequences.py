import unittest
import bandicoot as bc
from bandicoot.tests.generate_user import random_burst

from datetime import timedelta
from bandicoot.helper.fixes import total_seconds


class InterEventsTests(unittest.TestCase):
    def setUp(self):
        self.user = bc.User()

    def test_empty_interevents(self):
        self.user.records = []
        interevents = bc.individual.interevents_time(self.user)
        self.assertEqual(interevents['text'].values(), [None] * 2)

    def test_sequence_interevents(self):
        # 10 minutes burst
        _delta = timedelta(hours=2, minutes=13)
        self.user.records = random_burst(100, interaction='text',
                                         delta=_delta)
        interevents = bc.individual.interevents_time(self.user, groupby=None)
        self.assertEqual(interevents['text']['mean'],
                         total_seconds(_delta))
        self.assertEqual(interevents['text']['std'], 0)

        _delta = timedelta(hours=10, minutes=10)
        self.user.records = random_burst(100, interaction='text',
                                         delta=_delta)
        interevents = bc.individual.interevents_time(self.user, groupby=None)
        self.assertEqual(interevents['text']['mean'],
                         total_seconds(_delta))
