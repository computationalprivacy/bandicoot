"""
Automatic regression tests
"""

import bandicoot as bc
import unittest
from testing_tools import parse_dict, metric_suite
import os


ARGS = {'flatten': True, 'summary': 'extended', 'split_week': True, 'split_day': True}


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
        self.network_ego = bc.read_csv('ego', 'samples/network', 'samples/towers.csv', attributes_path='samples/attributes', network=True, warnings=False, describe=False)

        # Manual users
        self.user_a = bc.read_csv('A', 'samples/manual', 'samples/towers.csv', network=False, warnings=False, describe=False)
        self.user_a_network = bc.read_csv('A', 'samples/manual', 'samples/towers.csv', attributes_path='samples/attributes', network=True, warnings=False, describe=False)
        self.user_a_orange = bc.io.read_orange('A_orange', 'samples/manual', network=False, warnings=False, describe=False)
        self.user_a_orange_network = bc.io.read_orange('A_orange', 'samples/manual', network=True, attributes_path='samples/attributes', warnings=False, describe=False)

    def test_empty_user_all(self):
        self.assertTrue(*metric_suite(self.empty_user, parse_dict("samples/regressions/empty_user.json")['null'], **ARGS))

    def test_sample_user(self):
        self.assertTrue(*metric_suite(self.sample_user, parse_dict("samples/regressions/sample_user.json")['sample_user'], groupby=None, **ARGS))
            
    def test_network_ego(self):
        self.assertTrue(*metric_suite(self.network_ego, parse_dict("samples/regressions/ego.json")['ego'], **ARGS))

    def test_manual(self):
        result = parse_dict("samples/regressions/manual_a.json")['A']
        result.pop('name')
        result.pop('reporting__antennas_path')

        network_result = parse_dict("samples/regressions/manual_a_orange_network.json")['A_orange']
        network_result.pop('name')
        network_result.pop('reporting__antennas_path')
        self.assertTrue(*metric_suite(self.user_a, result, **ARGS))
        self.assertTrue(*metric_suite(self.user_a_orange, result, **ARGS))
        self.assertTrue(*metric_suite(self.user_a_orange_network, network_result, network=True,  **ARGS))
        self.assertTrue(*metric_suite(self.user_a_network, network_result, network=True, **ARGS))
    def _generate(self):
        bc.io.to_json(bc.utils.all(self.empty_user, **ARGS),
                      'samples/regressions/empty_user.json')
        bc.io.to_json(bc.utils.all(self.sample_user, groupby=None, **ARGS),
                      'samples/regressions/sample_user.json')
        bc.io.to_json(bc.utils.all(self.network_ego, **ARGS),
                      'samples/regressions/ego.json')
        bc.io.to_json(bc.utils.all(self.user_a, network=True, **ARGS),
                      'samples/regressions/manual_a.json')
        bc.io.to_json(bc.utils.all(self.user_a_orange_network, network=True, **ARGS),
                      'samples/regressions/manual_a_orange_network.json')
if __name__ == '__main__':
    t = TestRegressions('_generate')
    t.setUp()
    t._generate()
