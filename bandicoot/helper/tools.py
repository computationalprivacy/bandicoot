from collections import OrderedDict as NativeOrderedDict
from functools import update_wrapper
from datetime import timedelta
import itertools
import inspect
import json
import string


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        from bandicoot.core import User
        if isinstance(obj, User):
            return repr(obj)

        return json.JSONEncoder.default(self, obj)


class OrderedDict(NativeOrderedDict):
    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)

        # This solution is easy to implement but not robust
        s = json.dumps(self, cls=CustomEncoder, indent=4)

        transformations = [
            ('"<', '<'),
            ('>"', '>'),
            ('null', 'None')
        ]

        for old_pattern, new_pattern in transformations:
            s = s.replace(old_pattern, new_pattern)

        return s


def advanced_wrap(f, wrapper):
    """
    Wrap a decorated function while keeping the same keyword arguments
    """
    f_sig = list(inspect.getargspec(f))
    wrap_sig = list(inspect.getargspec(wrapper))

    # Update the keyword arguments of the wrapper
    if f_sig[3] is None or f_sig[3] == []:
        f_sig[3], f_kwargs = [], []
    else:
        f_kwargs = f_sig[0][-len(f_sig[3]):]

    for key, default in zip(f_kwargs, f_sig[3]):
        wrap_sig[0].append(key)
        wrap_sig[3] = wrap_sig[3] + (default, )

    wrap_sig[2] = None  # Remove kwargs
    src = "lambda %s: " % (inspect.formatargspec(*wrap_sig)[1:-1])
    new_args = inspect.formatargspec(
        wrap_sig[0], wrap_sig[1], wrap_sig[2], f_kwargs,
        formatvalue=lambda x: '=' + x)
    src += 'wrapper%s\n' % new_args

    decorated = eval(src, locals())
    return update_wrapper(decorated, f)


class Colors:
    """
    The `Colors` class stores six codes to color a string. It can be used to print
    messages inside a terminal prompt.

    Examples
    --------
    >>> print Colors.FAIL + "Error: it's a failure!" + Colors.ENDC

    Attributes
    ----------
    HEADER
        Header color.
    OKBLUE
        Blue color for a success message
    OKGREEN
        Green color for a success message
    WARNING
        Warning color (yellow)
    FAIL
        Failing color (red)
    ENDC
        Code to disable coloring. Always add it after coloring a string.

    """

    def __init__(self):
        pass

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'


def warning_str(str):
    """
    Return a colored string using the warning color (`Colors.WARNING`).
    """
    return Colors.WARNING + str + Colors.ENDC


def percent_records_missing_location(user, method=None):
    """
    Return the percentage of records missing a location parameter.
    """

    if len(user.records) == 0:
        return 0.

    missing_locations = sum([1 for record in user.records if record.position._get_location(user) is None])
    return float(missing_locations) / len(user.records)


def percent_overlapping_calls(records, min_gab=300):
    """
    Return the percentage of calls that overlap with the next call.

    Parameters
    ----------
    records : list
        The records for a single user.
    min_gab : int
        Number of seconds that the calls must overlap to be considered an issue.
        Defaults to 5 minutes.
    """

    calls = filter(lambda r: r.interaction == "call", records)

    if len(calls) == 0:
        return 0.

    overlapping_calls = 0
    for i, r in enumerate(calls):
        if i <= len(calls) - 2:
            if r.datetime + timedelta(seconds=r.call_duration - min_gab) >= calls[i + 1].datetime:
                overlapping_calls += 1

    return (float(overlapping_calls) / len(calls))


def antennas_missing_locations(user, Method=None):
    """
    Return the number of antennas missing locations in the records of a given user.
    """
    unique_antennas = set([record.position.antenna for record in user.records
                           if record.position.antenna is not None])
    return sum([1 for antenna in unique_antennas if user.antennas.get(antenna) is None])


def pairwise(iterable):
    """
    Returns pairs from an interator: s -> (s0,s1), (s1,s2), (s2, s3)...
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


class AutoVivification(dict):
    """
    Implementation of perl's autovivification feature.

    Under CC-BY-SA 3.0 from nosklo on stackoverflow:
    http://stackoverflow.com/questions/19189274/defaultdict-of-defaultdict-nested
    """

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

    def insert(self, keys, value):
        if len(keys) == 1:
            self[keys[0]] = value
        else:
            self[keys[0]].insert(keys[1:], value)


def get_template(filepath):
    with open(filepath, 'r') as f:
        file_string = f.read()
    return string.Template(file_string)
