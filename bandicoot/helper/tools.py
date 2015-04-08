from collections import OrderedDict as NativeOrderedDict
from functools import update_wrapper
import itertools
import inspect
import math


try:
    from thread import get_ident as _get_ident
except ImportError:
    from dummy_thread import get_ident as _get_ident


try:
    next
except NameError:
    from bandicoot.helper.fixes import next


class OrderedDict(NativeOrderedDict):
    def __repr__(self, _repr_running={}):
        'od.__repr__() <==> repr(od)'
        call_key = id(self), _get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1

        def _ordered_str_items(obj, offset=0):
            offset_space = ' ' * offset
            s = ""
            for key, value in obj:
                s += offset_space + "%r: %r,\n" % (key, value)
            return "{" + (s[offset:-2] if len(s) > 0 else s) + "}"

        try:
            if not self:
                return '%s()' % (self.__class__.__name__,)
            offset = len(self.__class__.__name__) + 2
            return '%s(%s)' % (self.__class__.__name__, _ordered_str_items(self.items(), offset))
        finally:
            del _repr_running[call_key]


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


def _winsorize(data, limit=0.99):
    """
    Returns a `Winsorized <http://en.wikipedia.org/wiki/Winsorising>` version of the input list.

    Examples
    --------

    With `limit=0.8`, 10% of the start and 10% of the end of ``data`` are _censored_.

    >>> _winsorize([1, 2, 3, 4, 5, 6, 7, 8, 9, 100], limit=0.8)
    [2, 2, 3, 4, 5, 6, 7, 8, 9, 9]

    With `limit=1.`, the list is returned untouched.

    >>> _winsorize([1, 2, 3, 4, 5, 6, 7, 8, 9, 100], limit=1.)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]

    """
    data = sorted(data)  # copy and sort data
    percentile = int(math.floor(len(data) * (1. - limit) * 0.5 + 1e-4))

    for i in xrange(percentile):
        data[i] = data[percentile]
        data[len(data) - 1 - i] = data[len(data) - 1 - percentile]

    return data


def percent_records_missing_location(user, method=None):
    """
    Return the percentage of records missing a location parameter.
    """

    if len(user.records) == 0:
        return 0.

    missing_locations = sum([1 for record in user.records if record.position._get_location(user) is None])
    return float(missing_locations) / len(user.records)


def antennas_missing_locations(user, Method=None):
    unique_antennas = set([record.position.antenna for record in user.records if record.position.antenna is not None])
    return sum([1 for antenna in unique_antennas if user.antennas.get(antenna) is None])


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def mean(data, limit=0.99, winsorize=True):

    """
    Return a winsorized arithmetic mean of ``data``.
    If ``limit=1``, it returns the classical mean.

    Examples
    --------

    >>> mean([1, 2, 3, 4, 4], limit=1)
    2.8

    In the following example, the first and last value of the list
    are replaced by their next value.

    >>> mean([1, 2, 3, 4, 5, 6, 7, 8, 9, 100], limit=0.8)
    5.5
    >>> mean([1, 2, 3, 4, 5, 6, 7, 8, 9, 100], limit=1.)
    14.5

    """

    if len(data) < 1:
        return None

    if winsorize:
        data = _winsorize(data, limit=limit)

    return float(sum(data)) / len(data)


def kurtosis(data):
    """
    Return the kurtosis for ``data``.
    """

    if len(data) == 0:
        return None

    num = moment(data, 4)
    denom = moment(data, 2) ** 2.

    return num / denom if denom != 0 else 0


def skewness(data):
    """
    Returns the skewness of ``data``.
    """

    if len(data) == 0:
        return None

    num = moment(data, 3)
    denom = moment(data, 2) ** 1.5

    return num / denom if denom != 0 else 0.


def std(data, winsorize=True, limit=0.99):
    if winsorize:
        data = _winsorize(data, limit=limit)

    if len(data) == 0:
        return None

    variance = moment(data, 2)
    return variance ** 0.5


def moment(data, n):
    if len(data) <= 1:
        return 0

    _mean = mean(data, winsorize=False)
    return float(sum([(item - _mean)**n for item in data])) / len(data)


def median(data):
    """
    Return the median of numeric data, unsing the "mean of middle two" method.
    If ``data`` is empty, ``0`` is returned.

    Examples
    --------

    >>> median([1, 3, 5])
    3.0

    When the number of data points is even, the median is interpolated:
    >>> median([1, 3, 5, 7])
    4.0
    """

    if len(data) == 0:
        return None

    data.sort()
    return float((data[len(data) / 2] + data[(len(data) - 1) / 2]) / 2.)


def minimum(data):
    if len(data) == 0:
        return None

    return float(min(data))


def maximum(data):
    if len(data) == 0:
        return None

    return float(max(data))


class SummaryStats(object):
    """
    Data structure storing a numeric distribution

    Attributes
    ----------
    mean : float
        Mean of the distribution.
    std : float
        The standard deviation of the distribution.
    min: float
        The minimum value of the distribution.
    max: float
        The max value of the distribution.
    median : float
        The median value of the distribution
    skewness : float
        The skewness of the distribution, measuring its asymmetry
    kurtosis : float
        The kurtosis of the distribution, measuring its "peakedness"
    distribution : list
        The complete distribution, as a list of floats

    Note
    ----

    You can generate a *SummaryStats* object using the
    :meth:`~bandicoot.helper.tools.summary_stats` function.

    """

    __slots__ = ['mean', 'std', 'min', 'max', 'median', 'skewness', 'kurtosis', 'distribution']

    def __init__(self, mean, std, min, max, median, skewness, kurtosis, distribution):
        self.mean, self.std, self.min, self.max, self.median, self.skewness, self.kurtosis, self.distribution = mean, std, min, max, median, skewness, kurtosis, distribution

    def __repr__(self):
        return "SummaryStats(" + ", ".join(map(lambda x: "%s=%r" % (x, getattr(self, x)), self.__slots__)) + ")"

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.__slots__ == other.__slots__:
            return all(getattr(self, attr) == getattr(other, attr) for attr in self.__slots__)
        return False


def summary_stats(data, winsorize=True, limit=0.99):
    """
    Returns a :class:`~bandicoot.helper.tools.SummaryStats` object containing informations on the given distribution.

    By default, the distribution is winsorized at 99%.

    Example
    -------
    >>> summary_stats([0, 1], winsorize=False)
    SummaryStats(mean=0.5, std=0.5, min=0.0, max=1.0, median=0.5, skewness=0.0, kurtosis=1.0, distribution=[0, 1])

    """

    if len(data) < 1:
        return SummaryStats(0., 0., 0., 0., 0., 0., 0., [])

    data.sort()
    _median = median(data)

    if winsorize:
        data = _winsorize(data, limit=limit)

    _mean = mean(data, winsorize=False)
    _std = std(data, winsorize=False)
    _minimum = minimum(data)
    _maximum = maximum(data)
    _kurtosis = kurtosis(data)
    _skewness = skewness(data)
    _distribution = data

    return SummaryStats(_mean, _std, _minimum, _maximum, _median, _skewness, _kurtosis, _distribution)


def entropy(data):
    """
    Compute the Shannon entropy, a measure of uncertainty.
    """

    if len(data) == 0:
        return None

    n = sum(data)

    _op = lambda f: f * math.log(f)
    return - sum(_op(float(i) / n) for i in data)


def great_circle_distance(pt1, pt2):
    r = 6371.

    delta_latitude = (pt1[0]-pt2[0])/180*math.pi
    delta_longitude = (pt1[1]-pt2[1])/180*math.pi
    latitude1 = pt1[0]/180*math.pi
    latitude2 = pt2[0]/180*math.pi

    return r*2.*math.asin(math.sqrt(math.pow(math.sin(delta_latitude/2), 2) + math.cos(latitude1)*math.cos(latitude2) * math.pow(math.sin(delta_longitude/2), 2)))
