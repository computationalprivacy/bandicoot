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

from collections import OrderedDict as NativeOrderedDict
from functools import update_wrapper
from datetime import timedelta
import itertools
import inspect
import json
import logging
import hashlib
import sys
import os


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

    def _repr_pretty_(self, p, cycle):
        p.text(self.__repr__())


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
    decorated.func = f
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


class _AnsiColorizer(object):
    """
    A colorizer is an object that loosely wraps around a stream, allowing
    callers to write text to the stream in a particular color.

    Colorizer classes must implement C{supported()} and C{write(text, color)}.
    """
    _colors = dict(black=30, red=31, green=32, yellow=33,
                   blue=34, magenta=35, cyan=36, white=37)

    def __init__(self, stream):
        self.stream = stream

    @classmethod
    def supported(cls, stream=sys.stdout):
        """
        A class method that returns True if the current platform supports
        coloring terminal output using this method. Returns False otherwise.
        """
        if not stream.isatty():
            return False  # auto color only on TTYs
        try:
            import curses
        except ImportError:
            return False
        else:
            try:
                try:
                    return curses.tigetnum("colors") > 2
                except curses.error:
                    curses.setupterm()
                    return curses.tigetnum("colors") > 2
            except:
                raise
                # guess false in case of error
                return False

    def write(self, text, color):
        """
        Write the given text to the stream in the given color.
        """
        color = self._colors[color]
        self.stream.write('\x1b[{}m{}\x1b[0m'.format(color, text))


class ColorHandler(logging.StreamHandler):
    def __init__(self, stream=sys.stderr):
        super(ColorHandler, self).__init__(_AnsiColorizer(stream))

    def emit(self, record):
        msg_colors = {
            logging.DEBUG: ("Debug", "green"),
            logging.INFO: ("Info", "blue"),
            logging.WARNING: ("Warning", "yellow"),
            logging.ERROR: ("Error", "red")
        }

        header, color = msg_colors.get(record.levelno, "blue")
        if 'prefix' in record.__dict__:
            header = record.prefix
        else:
            header = header + ':'
        self.stream.write("{} {}\n".format(header, record.msg), color)


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

    calls = [r for r in records if r.interaction == "call"]

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
    return zip(a, b)


class AutoVivification(OrderedDict):
    """
    Implementation of perl's autovivification feature.

    Under CC-BY-SA 3.0 from nosklo on stackoverflow:
    http://stackoverflow.com/questions/19189274/defaultdict-of-defaultdict-nested
    """

    def __getitem__(self, item):
        try:
            return OrderedDict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

    def insert(self, keys, value):
        if len(keys) == 1:
            self[keys[0]] = value
        else:
            self[keys[0]].insert(keys[1:], value)


MAIN_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bandicoot_code_signature():
    """
    Returns a unique hash of the Python source code in the current bandicoot
    module, using the cryptographic hash function SHA-1.
    """
    checksum = hashlib.sha1()

    for root, dirs, files in os.walk(MAIN_DIRECTORY):
        for filename in sorted(files):
            if not filename.endswith('.py'):
                continue

            f_path = os.path.join(root, filename)
            f_size = os.path.getsize(f_path)
            with open(f_path, 'rb') as f:
                while f.tell() != f_size:
                    checksum.update(f.read(0x40000))

    return checksum.hexdigest()
