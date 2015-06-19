#!/usr/bin/python

import math

from bandicoot.helper.group import spatial_grouping, group_records
from bandicoot.helper.tools import entropy, great_circle_distance, summary_stats
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

    target = math.ceil(sum(location_count.values()) * percentage)
    location_sort = sorted(location_count.keys(),
                           key=lambda x: location_count[x])

    while target > 0 and len(location_sort) > 0:
        location_id = location_sort.pop()
        target -= location_count[location_id]

    return len(location_count) - len(location_sort)


def spatial_diversity(records, interaction=None):
    """
    Geographic diversity in the antennas as a function of the Shannon entropy.
    Can be calculated weighted with call, text, call duration, or None (total calls and texts).
    Unweighted is equivalent to entropy_of_antennas().
    """
    records = list(records)

    if len(records) == 0:
        return None

    interactions = defaultdict(list)
    counter = Counter()
   
    for r in records:
        if interaction == 'call_duration':
            interactions[r.position].append(r.call_duration)
        elif interaction == 'call' and r.interaction == 'call':
            interactions[r.position].append(1)
        else:
            interactions[r.position].append(1)
    for i in interactions.items():
        interactions[i[0]] = sum(i[1])
    
    return entropy(interactions.values()) / math.log(len(interactions.values()))


def tower_churn_rate(user):
    """
    The cosine distance between the frequency spent at each tower each week.
    """
    if len(user.records) == 0:
        return None

    iter = group_records(user, groupby='week')
    weekly_records = [[r for r in l] for l in iter]

    positions = [r.position for r in user.records]
    antennas = {}
    cos_dist = []
    for i in list(set(positions)):
        antennas[i] = [0] * len(weekly_records)
    for week in range(len(weekly_records)):
        for r in weekly_records[week]:
            antennas[r.position][week] += 1. / len(weekly_records[week])
    for i in range(len(weekly_records)-1):
        num = sum(a[i] * a[i+1] for a in antennas.values())
        denoma = sum(a[i] ** 2 for a in antennas.values())
        denomb = sum(b[i+1] ** 2 for b in antennas.values())
        cos_dist.append(1 - num / (denoma ** .5 * denomb ** .5))

    return summary_stats(cos_dist)
