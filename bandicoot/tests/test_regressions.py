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
Automatic regression tests
"""

import bandicoot as bc
import unittest
from .testing_tools import parse_dict, metric_suite, compare_dict
import os
import logging
logging.disable(logging.CRITICAL)


ARGS = {
    'flatten': True,
    'summary': 'extended',
    'split_week': True,
    'split_day': True
}


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
        self.network_ego = bc.read_csv(
            'ego', 'samples/network', 'samples/towers.csv',
            attributes_path='samples/attributes', network=True, describe=False)

        # Manual users
        self.user_a = bc.read_csv(
            'A', 'samples/manual', 'samples/towers.csv',
            recharges_path='samples/manual/recharges', network=False,
            describe=False)
        self.user_a_network = bc.read_csv(
            'A', 'samples/manual', 'samples/towers.csv',
            attributes_path='samples/attributes', network=True, describe=False)
        self.user_a_orange = bc.io.read_orange(
            'A_orange', 'samples/manual', 'sample/towers.csv',
            recharges_path='samples/manual/recharges', network=False,
            describe=False)
        self.user_a_orange_network = bc.io.read_orange(
            'A_orange', 'samples/manual', network=True,
            attributes_path='samples/attributes', describe=False)

    def test_empty_user_all(self):
        self.assertTrue(*metric_suite(self.empty_user,
                                      parse_dict("samples/regressions/empty_user.json")['null'], **ARGS))

    def test_sample_user(self):
        print(self.sample_user.percent_outofnetwork_calls)
        self.assertTrue(*metric_suite(self.sample_user, parse_dict(
            "samples/regressions/sample_user.json")['sample_user'], groupby=None, **ARGS))

    def test_network_ego(self):
        self.assertTrue(*metric_suite(self.network_ego,
                                      parse_dict("samples/regressions/ego.json")['ego'], **ARGS))

    def test_manual(self):
        result = parse_dict("samples/regressions/manual_a.json")['A']
        result.pop('name')
        result.pop('reporting__antennas_path')
        result.pop('reporting__number_of_antennas')

        network_result = parse_dict(
            "samples/regressions/manual_a_orange_network.json")['A_orange']
        network_result.pop('name')
        network_result.pop('reporting__antennas_path')
        network_result.pop('reporting__number_of_antennas')
        self.assertTrue(*metric_suite(self.user_a, result, **ARGS))
        self.assertTrue(*metric_suite(self.user_a_orange, result, **ARGS))
        self.assertTrue(
            *metric_suite(self.user_a_orange_network, network_result, network=True, **ARGS))
        self.assertTrue(
            *metric_suite(self.user_a_network, network_result, network=True, **ARGS))

    def test_dashboard(self):
        rv = bc.visualization.user_data(self.sample_user)
        baseline = parse_dict('samples/regressions/dashboard_sample_user.json')
        self.assertTrue(*compare_dict(rv, baseline['me']))

    def test_dashboard_export(self):
        export_path = bc.visualization.export(self.sample_user)
        json_path = os.path.join(export_path, 'data/bc_export.json')
        rv = parse_dict(json_path)
        baseline = parse_dict('samples/regressions/dashboard_sample_user.json')
        self.assertTrue(*compare_dict(rv['me'], baseline['me']))

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

        rv = bc.visualization.user_data(self.sample_user)
        bc.io.to_json(rv, 'samples/regressions/dashboard_sample_user.json')


if __name__ == '__main__':
    t = TestRegressions('_generate')
    t.setUp()
    t._generate()
