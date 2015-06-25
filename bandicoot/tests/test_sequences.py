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
        self.assertEqual(interevent['allweek']['allday']['text'].values(), [None] * 2)

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
