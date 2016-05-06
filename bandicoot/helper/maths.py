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

from __future__ import division
import math


def mean(data):
    """
    Return the arithmetic mean of ``data``.

    Examples
    --------

    >>> mean([1, 2, 3, 4, 4])
    2.8
    """

    if len(data) < 1:
        return None

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


def std(data):
    if len(data) == 0:
        return None

    variance = moment(data, 2)
    return variance ** 0.5


def moment(data, n):
    if len(data) <= 1:
        return 0

    _mean = mean(data)
    return float(sum([(item - _mean) ** n for item in data])) / len(data)


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

    data = sorted(data)
    return float((data[len(data) // 2] + data[(len(data) - 1) // 2]) / 2.)


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
    Data structure storing a numeric distribution.

    .. note:: You can generate a *SummaryStats* object using the
              :meth:`~bandicoot.helper.maths.summary_stats` function.

    Attributes
    ----------
    mean : float
        Mean of the distribution.
    std : float
        The standard deviation of the distribution.
    min : float
        The minimum value of the distribution.
    max : float
        The max value of the distribution.
    median : float
        The median value of the distribution
    skewness : float
        The skewness of the distribution, measuring its asymmetry
    kurtosis : float
        The kurtosis of the distribution, measuring its "peakedness"
    distribution : list
        The complete distribution, as a list of floats
    """
    __slots__ = ['mean', 'std', 'min', 'max', 'median',
                 'skewness', 'kurtosis', 'distribution']

    def __init__(self, mean, std, min, max, median, skewness, kurtosis, distribution):
        self.mean, self.std, self.min, self.max, self.median, self.skewness, self.kurtosis, self.distribution = mean, std, min, max, median, skewness, kurtosis, distribution

    def __repr__(self):
        return "SummaryStats(" + ", ".join(["%s=%r" % (x, getattr(self, x)) for x in self.__slots__]) + ")"

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.__slots__ == other.__slots__:
            return all(getattr(self, attr) == getattr(other, attr) for attr in self.__slots__)
        return False


def summary_stats(data):
    """
    Returns a :class:`~bandicoot.helper.maths.SummaryStats` object
    containing statistics on the given distribution.

    Examples
    --------
    >>> summary_stats([0, 1])
    SummaryStats(mean=0.5, std=0.5, min=0.0, max=1.0, median=0.5, skewness=0.0, kurtosis=1.0, distribution=[0, 1])
    """

    if data is None:
        data = []
    data = sorted(data)

    if len(data) < 1:
        return SummaryStats(None, None, None, None, None, None, None, [])

    _median = median(data)

    _mean = mean(data)
    _std = std(data)
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
    """
    Return the great-circle distance in kilometers between two points, defined by a tuple (lat, lon).

    Examples
    --------
    >>> brussels = (50.8503, 4.3517)
    >>> paris = (48.8566, 2.3522)
    >>> great_circle_distance(brussels, paris)
    263.9754164080347
    """
    r = 6371.

    delta_latitude = math.radians(pt1[0] - pt2[0])
    delta_longitude = math.radians(pt1[1] - pt2[1])
    latitude1 = math.radians(pt1[0])
    latitude2 = math.radians(pt2[0])

    a = math.sin(delta_latitude / 2) ** 2 + math.cos(latitude1) * math.cos(latitude2) * math.sin(delta_longitude / 2) ** 2
    return r * 2. * math.asin(math.sqrt(a))
