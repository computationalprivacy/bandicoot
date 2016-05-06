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

from .helper.group import spatial_grouping, grouping_query, statistics
from .helper.maths import entropy, great_circle_distance
from .helper.tools import pairwise
from collections import Counter, OrderedDict


@spatial_grouping(user_kwd=True)
def percent_at_home(positions, user):
    """
    The percentage of interactions the user had while he was at home.

    .. note::
        The position of the home is computed using
        :meth:`User.recompute_home <bandicoot.core.User.recompute_home>`.
        If no home can be found, the percentage of interactions at home
        will be ``None``.
    """

    if not user.has_home:
        return None

    total_home = sum(1 for p in positions if p == user.home)
    return float(total_home) / len(positions) if len(positions) != 0 else 0


@spatial_grouping(user_kwd=True)
def radius_of_gyration(positions, user):
    """
    Returns the radius of gyration, the *equivalent distance* of the mass from
    the center of gravity, for all visited places. [GON2008]_

    References
    ----------
    .. [GON2008] Gonzalez, M. C., Hidalgo, C. A., & Barabasi, A. L. (2008).
        Understanding individual human mobility patterns. Nature, 453(7196),
        779-782.
    """
    d = Counter(p._get_location(user) for p in positions
                if p._get_location(user) is not None)
    sum_weights = sum(d.values())
    positions = list(d.keys())  # Unique positions

    if len(positions) == 0:
        return None

    barycenter = [0, 0]
    for pos, t in d.items():
        barycenter[0] += pos[0] * t
        barycenter[1] += pos[1] * t

    barycenter[0] /= sum_weights
    barycenter[1] /= sum_weights

    r = 0.
    for pos, t in d.items():
        r += float(t) / sum_weights * \
            great_circle_distance(barycenter, pos) ** 2
    return math.sqrt(r)


@spatial_grouping
def entropy_of_antennas(positions, normalize=False):
    """
    The entropy of visited antennas.

    Parameters
    ----------
    normalize: boolean, default is False
        Returns a normalized entropy between 0 and 1.
    """
    counter = Counter(p for p in positions)
    raw_entropy = entropy(list(counter.values()))
    n = len(counter)
    if normalize and n > 1:
        return raw_entropy / math.log(n)
    else:
        return raw_entropy


@spatial_grouping
def number_of_antennas(positions):
    """
    The number of unique places visited.
    """
    return len(set(positions))


@spatial_grouping
def frequent_antennas(positions, percentage=0.8):
    """
    The number of location that account for 80% of the locations where the user was.
    Percentage can be supplied as a decimal (e.g., .8 for default 80%).
    """
    location_count = Counter(list(map(str, positions)))

    target = math.ceil(sum(location_count.values()) * percentage)
    location_sort = sorted(list(location_count.keys()),
                           key=lambda x: location_count[x])

    while target > 0 and len(location_sort) > 0:
        location_id = location_sort.pop()
        target -= location_count[location_id]

    return len(location_count) - len(location_sort)


def churn_rate(user, summary='default', **kwargs):
    """
    Computes the frequency spent at every towers each week, and returns the
    distribution of the cosine similarity between two consecutives week.

    .. note:: The churn rate is always computed between pairs of weeks.
    """
    if len(user.records) == 0:
        return statistics([], summary=summary)

    query = {
        'groupby': 'week',
        'divide_by': OrderedDict([
            ('part_of_week', ['allweek']),
            ('part_of_day', ['allday'])
        ]),
        'using': 'records',
        'filter_empty': True,
        'binning': True
    }

    rv = grouping_query(user, query)
    weekly_positions = rv[0][1]

    all_positions = list(set(p for l in weekly_positions for p in l))
    frequencies = {}
    cos_dist = []

    for week, week_positions in enumerate(weekly_positions):
        count = Counter(week_positions)
        total = sum(count.values())
        frequencies[week] = [count.get(p, 0) / total for p in all_positions]

    all_indexes = range(len(all_positions))
    for f_1, f_2 in pairwise(list(frequencies.values())):
        num = sum(f_1[a] * f_2[a] for a in all_indexes)
        denom_1 = sum(f ** 2 for f in f_1)
        denom_2 = sum(f ** 2 for f in f_2)
        cos_dist.append(1 - num / (denom_1 ** .5 * denom_2 ** .5))

    return statistics(cos_dist, summary=summary)
