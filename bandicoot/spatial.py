#!/usr/bin/python

import math

from bandicoot.helper.group import spatial_grouping
from bandicoot.helper.tools import entropy, great_circle_distance
from bandicoot.helper.fixes import Counter


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
def entropy_of_antennas(positions):
    """
    The entropy of visited antennas.
    """
    counter = Counter(p for p in positions)
    return entropy(counter.values())


@spatial_grouping(use_records=True)
def number_of_antennas(records):
    """
    The number of unique places visited.
    """
    return len(set(r.position for r in records))


@spatial_grouping
def frequent_antennas(positions, percentage=0.8):
    """
    The number of location that account for 80% of the locations where the user was.
    """
    location_count = Counter(map(str, positions))

    target = int(math.floor(sum(location_count.values()) * percentage))
    location_sort = sorted(location_count.keys(),
                           key=lambda x: location_count[x])

    while target > 0 and len(location_sort) > 0:
        location_id = location_sort.pop()
        target -= location_count[location_id]

    return len(location_count) - len(location_sort)
