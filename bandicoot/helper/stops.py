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

from bandicoot.helper.maths import great_circle_distance
import itertools


def compute_distance_matrix(points):
    """
    Return a matrix of distance (in meters) between every point in a given list
    of (lat, lon) location tuples.
    """
    n = len(points)
    return [[1000 * great_circle_distance(points[i], points[j])
             for j in range(n)] for i in range(n)]


def get_neighbors(distance_matrix, source, eps):
    """
    Given a matrix of distance between couples of points,
    return the list of every point closer than eps from a certain point.
    """

    return [dest for dest, distance in enumerate(distance_matrix[source]) if distance < eps]


def dbscan(points, eps, minpts):
    """
    Implementation of [DBSCAN]_ (*A density-based algorithm for discovering
    clusters in large spatial databases with noise*). It accepts a list of
    points (lat, lon) and returns the labels associated with the points.

    References
    ----------
    .. [DBSCAN] Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996, August).
        A density-based algorithm for discovering clusters in large
        spatial databases with noise. In Kdd (Vol. 96, No. 34, pp. 226-231).

    """
    next_label = 0
    n = len(points)
    labels = [None] * n

    distance_matrix = compute_distance_matrix(points)
    neighbors = [get_neighbors(distance_matrix, i, eps) for i in range(n)]

    for i in range(n):
        if labels[i] is not None:
            continue

        if len(neighbors[i]) < minpts:
            continue

        labels[i] = next_label
        candidates = [i]
        while len(candidates) > 0:
            c = candidates.pop()

            for j in neighbors[c]:
                if labels[j] is None:
                    labels[j] = next_label
                    if len(neighbors[j]) >= minpts:
                        candidates.append(j)

        next_label += 1

    return labels


def _groupwhile(x, fwhile):
    groups = []
    i = 0
    while i < len(x):
        j = i
        while j < len(x) - 1 and fwhile(i, j + 1):
            j = j + 1
        groups.append(x[i:j + 1])
        i = j + 1
    return groups


def get_stops(records, group_dist):
    """
    Group records arounds stop locations and returns a list of
    dict(location, records) for each stop.

    Parameters
    ----------
    records : list
        A list of Record objects ordered by non-decreasing datetime
    group_dist : float
        Minimum distance (in meters) to switch to a new stop.
    """
    def traverse(start, next):
        position_prev = records[next - 1].position.location
        position_next = records[next].position.location
        dist = 1000 * great_circle_distance(position_prev, position_next)
        return dist <= group_dist

    groups = _groupwhile(records, traverse)

    def median(x):
        return sorted(x)[len(x) // 2]

    stops = []
    for g in groups:
        _lat = median([gv.position.location[0] for gv in g])
        _lon = median([gv.position.location[1] for gv in g])
        stops.append({
            'location': (_lat, _lon),
            'records': g,
        })

    return stops


def cluster_and_update(records, group_dist=50, eps=100):
    """
    Update records, by clustering their positions using the DBSCAN algorithm.
    Returns a dictionnary associating new antenna identifiers to (lat, lon)
    location tuples.

    .. note:: Use this function to cluster fine-grained GPS records.

    Parameters
    ----------
    records : list
        A list of Record objects ordered by non-decreasing datetime
    group_dist : float, default: 50
        Minimum distance (in meters) to switch to a new stop.
    eps : float, default: 100
        The eps parameter for the DBSCAN algorithm.
    """
    # Run the DBSCAN algorithm with all stop locations and 1 minimal point.
    stops = get_stops(records, group_dist)
    labels = dbscan([s['location'] for s in stops], eps, 1)

    # Associate all records with their new antenna
    antennas = {}
    for i, stop in enumerate(stops):
        antenna_id = labels[i]
        for record in stop['records']:
            record.position.antenna = antenna_id

        antennas[antenna_id] = stop['location']

    all_records = sum(len(stop['records']) for stop in stops)
    if all_records != len(records):
        raise ValueError("get_antennas has {} records instead of {} "
                         "initially.".format(all_records, len(records)))

    return antennas


def fix_location(records, max_elapsed_seconds=300):
    """
    Update position of all records based on the position of
    the closest GPS record.

    .. note:: Use this function when call and text records are missing a
              location, but you have access to accurate GPS traces.

    """
    groups = itertools.groupby(records, lambda r: r.direction)
    groups = [(interaction, list(g)) for interaction, g in groups]

    def tdist(t1, t2):
            return abs((t1 - t2).total_seconds())

    for i, (interaction, g) in enumerate(groups):
        if interaction == 'in':
            continue

        prev_gps = groups[i-1][1][-1]
        next_gps = groups[i+1][1][0]

        for r in g:
            if tdist(r.datetime, prev_gps.datetime) <= max_elapsed_seconds:
                r.position = prev_gps.position
            elif tdist(r.datetime, next_gps.datetime) <= max_elapsed_seconds:
                r.position = next_gps.position
