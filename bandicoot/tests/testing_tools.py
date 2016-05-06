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

import json
import filecmp
import bandicoot as bc
import numpy as np


def parse_dict(path):
    with open(path, 'r') as f:
        dict_data = json.load(f)
    return dict_data


def file_equality(f1, f2):
    '''Returns true if the files are the same.'''
    return filecmp.cmp(f1, f2)


def metric_suite(user, answers, decimal=7, **kwargs):
    '''
    Runs the complete metric suite.
    If any of the metrics is different than the expected answer, return False.
    '''

    results = bc.utils.all(user, **kwargs)
    test_result, msg = compare_dict(answers, results, decimal=decimal)
    return test_result, msg


def compare_dict(answer, result, decimal=7):
    '''Returns true if two dictionaries are approximately equal. Returns false otherwise.'''
    flat_answer = bc.utils.flatten(answer)
    flat_result = bc.utils.flatten(result)

    for key in flat_answer.keys():
        if key not in flat_result.keys():
            return False, "The key {} was not there.".format(key)

        answer_v, result_v = flat_answer[key], flat_result[key]

        if isinstance(answer_v, (float, int)) and isinstance(result_v, (float, int)):
            try:
                np.testing.assert_almost_equal(answer_v, result_v, decimal=decimal)
            except AssertionError:
                err_msg = "The key {} produced a different result: expected {}, got {}.".format(key, answer_v, result_v)
                return False, err_msg
        elif answer_v != result_v:
            return False, "The key {} produced a different result: expected {}, got {}.".format(key, answer_v, result_v)

    return True, ""
