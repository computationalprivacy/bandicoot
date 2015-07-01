from __future__ import division

import math

from .helper.group import spatial_grouping, group_records, statistics, _binning
from .helper.tools import entropy, great_circle_distance, pairwise
from collections import Counter
from collections import defaultdict


@spatial_grouping(user_kwd=True)
def percent_at_home(positions, user):
    """
    The percentage of interactions the user had while he was at home.

    Notes
    -----
    The position of the home is computed by :meth:`User.compute_home`.
    If no home can be found, the percentage at home will be ``None``.
    """

    if not user.has_home:
        return None
    if user.home.antenna is None and user.home.location is None:
        return None
    positions = list(positions)
    total_home = sum(1 for p in positions if p == user.home)
    return float(total_home) / len(positions) if len(positions) != 0 else 0


@spatial_grouping
def radius_of_movement(records):
    return NotImplemented


@spatial_grouping(user_kwd=True)
def radius_of_gyration(positions, user):
    """
    The radius of gyration.

    The radius of gyration is the *equivalent distance* of the mass from the
    center of gravity, for all visited places  [GON2008]_

    None is returned if there are no (lat, lon) positions for where the user has been.

    .. [GON2008] Gonzalez, M. C., Hidalgo, C. A., & Barabasi, A. L. (2008). Understanding individual human mobility patterns. Nature, 453(7196), 779-782.

    """

    d = Counter(p._get_location(user) for p in positions if p._get_location(user) is not None)
    sum_weights = sum(d.values())
    positions = d.keys()  # Unique positions

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
        r += float(t) / sum_weights * great_circle_distance(barycenter, pos) ** 2
        r += float(t) / sum_weights * great_circle_distance(barycenter, pos) ** 2
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
    raw_entropy = entropy(counter.values())
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
    location_count = Counter(map(str, positions))

    target = math.ceil(sum(location_count.values()) * percentage)
    location_sort = sorted(location_count.keys(),
                           key=lambda x: location_count[x])

    while target > 0 and len(location_sort) > 0:
        location_id = location_sort.pop()
        target -= location_count[location_id]

    return len(location_count) - len(location_sort)


def churn_rate(user, summary='default', **kwargs):
    """
    The cosine distance between the frequency spent at each tower each week.
    """

    if len(user.records) == 0:
        return None

    iter = group_records(user, groupby='week')
    weekly_positions = [list(_binning(l)) for l in iter]  # bin positions every 30 minutes

    all_positions = list(set(p for l in weekly_positions for p in l))
    frequencies = {}
    cos_dist = []

    for week, week_positions in enumerate(weekly_positions):
        count = Counter(week_positions)
        total = sum(count.values())
        frequencies[week] = [count.get(p, 0) / total for p in all_positions]

    all_indexes = xrange(len(all_positions))
    for f_1, f_2 in pairwise(frequencies.values()):
        num = sum(f_1[a] * f_2[a] for a in all_indexes)
        denom_1 = sum(f ** 2 for f in f_1)
        denom_2 = sum(f ** 2 for f in f_2)
        cos_dist.append(1 - num / (denom_1 ** .5 * denom_2 ** .5))

    return statistics(cos_dist, summary=summary)
