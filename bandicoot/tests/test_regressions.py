"""
Automatic regression tests
"""

import bandicoot as bc
import unittest
from testing_tools import parse_dict
import os


class TestRegressions(unittest.TestCase):
    def setUp(self):
        if not getattr(TestRegressions, '_dir_changed', False):
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestRegressions._dir_changed = True

        self.empty_user = bc.User()
        self.empty_user.attributes['empty'] = True

        self.sample_user = bc.tests.generate_user.sample_user()

        self.network_ego = bc.read_csv('ego', 'samples/network', 'samples/towers.csv', warnings=False, describe=False)

    def test_empty_user_all(self):
        result = bc.utils.all(self.empty_user, summary='extended', split_week=True, split_day=True, flatten=True)
        self.assertDictEqual(dict(result), parse_dict("samples/regressions/empty_user.json")['null'])

    def test_sample_user(self):
        result = bc.utils.all(self.sample_user, groupby=None, summary='extended', split_week=True, split_day=True, flatten=True)
        self.assertDictEqual(result, parse_dict("samples/regressions/sample_user.json")['sample_user'])

    def test_network_ego(self):
        result = bc.utils.all(self.network_ego, summary='extended', split_week=True, split_day=True, flatten=True)
        self.assertDictEqual(result, parse_dict("samples/regressions/ego.json")['ego'])

    def _generate(self):
        bc.io.to_json(bc.utils.all(self.empty_user, summary='extended', split_week=True, split_day=True, flatten=True),
                      'samples/regressions/empty_user.json')
        bc.io.to_json(bc.utils.all(self.sample_user, summary='extended', split_week=True, split_day=True, groupby=None, flatten=True),
                      'samples/regressions/sample_user.json')
        bc.io.to_json(bc.utils.all(self.network_ego, summary='extended', split_week=True, split_day=True, flatten=True),
                      'samples/regressions/ego.json')

if __name__ == '__main__':
    t = TestRegressions('_generate')
    t.setUp()
    t._generate()
