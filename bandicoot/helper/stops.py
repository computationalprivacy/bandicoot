from bandicoot.helper.maths import great_circle_distance

import bisect
import datetime


def compute_distance_matrix(points):
    """
    Return a matrix of distance (in meters) between every point in a given list
    of (lat, lon) tuples.
    """

    n = len(points)
    return [[1000 * great_circle_distance(points[i], points[j]) for j in range(n)]
            for i in range(n)]


def get_neighbors(distance_matrix, source, eps):
    """
    Given a matrix of distance between couples of points,
    return the list of every point closer than eps from a certain point.
    """

    return [dest for dest, distance in enumerate(distance_matrix[source]) if distance < eps]


def dbscan(points, eps, minpts):
    """
    Implementation of DBSCAN (A density-based algorithm for discovering
    clusters in large spatial databases with noise) It accepts a list of
    points (lat, lon) and returns the labels associated with the points.
    """

    next_label = 0

    n = len(points)
    distance_matrix = compute_distance_matrix(points)
    labels = [None] * n

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


def groupwhile(x, fwhile):
    groups = []
    i = 0
    while i < len(x):
        j = i
        while j < len(x) - 1 and fwhile(i, j + 1):
            j = j + 1
        groups.append(x[i:j + 1])
        i = j + 1
    return groups


def get_stops(records, group_dist, min_time=0):
    """
    Accept as input a sequence of Record objects ordered by non-decreasing timestamp.
    Returns a sequence of stops in the format dict(location, records)
    """

    groups = groupwhile(records, lambda start, next: (1000 * great_circle_distance(records[next - 1].position.location, records[next].position.location) <= group_dist))

    def median(x):
        return sorted(x)[len(x) // 2]

    stops = []
    for g in groups:
        delta_t = g[-1].datetime - g[0].datetime

        if delta_t >= datetime.timedelta(minutes=min_time):
            _lat = median([gv.position.location[0] for gv in g])
            _lon = median([gv.position.location[1] for gv in g])
            stops.append({
                'location': (_lat, _lon),
                'records': g,
            })

    return stops


def update_antennas(records, group_dist=50):
    """
    Takes an (ordered) list of Record objects and update their antenna id.
    Returns a dictionnary associating antenna_id to (lat, lon) locations.
    """

    # Run the DBSCAN algorithm with all stop locations, an epsilon value of
    # 100 meters, and 1 minimal point
    stops = get_stops(records, group_dist)
    labels = dbscan([s['location'] for s in stops], 100, 1)

    # Associate all records with their new antenna
    antennas = {}
    for i, stop in enumerate(stops):
        antenna_id = labels[i]
        for record in stop['records']:
            record.position.antenna = antenna_id

        antennas[antenna_id] = stop['location']

    all_records = sum(len(stop['records']) for stop in stops)
    if all_records != len(records):
        raise ValueError("get_antennas has {} records instead of {} initially.".format(all_records, len(records)))

    return antennas


def find_natural_antennas(records):
    # Get the antennas and add 'antenna_id' keys.
    antennas = update_antennas(records)

    def mapper(datetime, error=300):
        # perform a binary search on the positions to find the nearest
        # one. Try nearby indices to locate best one.
        i = bisect.bisect(records, (datetime,))
        offsets = [-1, 0, 1]
        candidates = []
        for k in offsets:
            try:
                c = records[k + i]
                candidates.append(c.datetime)
            except IndexError:
                pass

        tdist = lambda t1, t2: abs((t1 - t2).total_seconds())
        nearest = min(candidates, key=lambda c: tdist(c, datetime))

        # Return its antenna_id if it was 'close enough' in time:
        # by default, 5 minutes.
        if tdist(nearest, datetime) <= error:
            return nearest[1]["antenna_id"]

    return antennas, mapper
