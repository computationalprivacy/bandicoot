import json
import filecmp
import bandicoot as bc
import numpy as np


def _convert(input):
    """
    Recursive convertion of unicode
    """
    if isinstance(input, dict):
        return {_convert(key): _convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [_convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def parse_dict(path):
    data = open(path)
    dict_data = _convert(json.load(data))
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
