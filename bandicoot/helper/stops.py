from math import radians, cos, sin, asin, sqrt
from collections import defaultdict
import datetime

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    m = 6367000 * c
    return m

def compute_distance_matrix(points):
    d = defaultdict(dict)
    n = len(points)
    for i in range(n):
        for j in range(n):
            if i == j:
                d[i][j] = 0
            elif i > j:
                d[i][j] = d[j][i]
            else:
                d[i][j] = haversine(points[i][0],points[i][1],points[j][0],points[j][1])
    return d

def get_neighbors(distance_matrix, source, eps):
    return [dest for dest, distance in distance_matrix[source].items() if distance < eps]

def dbscan(points, eps, minpts):
    """
    Implementation of DBSCAN (A density-based algorithm for discovering clusters in large spatial databases with noise)

    Accepts a list of points (lon,lat) and returns the labels associated with the points
    """
    next_label = 0
    NOISE = -1
    n = len(points)
    distance_matrix = compute_distance_matrix(points)
    labels = [NOISE] * n
    for i in range(n):
        if labels[i] != NOISE:
            continue

        neighbors = get_neighbors(distance_matrix, i, eps)

        if len(neighbors) < minpts:
            continue

        labels[i] = next_label
        candidates = [i]
        while len(candidates) > 0:
            new_candidates = []
            for c in candidates:
                c_neighbors = get_neighbors(distance_matrix, c, eps)
                for j in c_neighbors:
                    if labels[j] == NOISE:
                        labels[j] = next_label
                        noise_neighbors = get_neighbors(distance_matrix, j, eps)
                        if len(noise_neighbors) >= minpts:
                            new_candidates.append(j)
            candidates = new_candidates
        next_label += 1
    return labels


def groupwhile(x, fwhile):
    groups = []
    i = 0
    while i < len(x):
        j = i
        while j < len(x) - 1 and fwhile(i, j+1):
            j = j + 1
        groups.append(x[i:j+1])
        i = j+1
    return groups


def median(x):
    return sorted(x)[len(x)//2]

def get_stops(locs, group_dist, min_time=0):
    """
    Accept as input a sequence of records in the format dict(timestamp, lon, lat) ordered by non-decreasing timestamp.
    Returns a sequence of stops in the format dict(lon,lat,arrival,departure)
    """
    assert(len(locs) > 0)
    groups = groupwhile(locs, lambda start, next: (haversine(locs[next-1]['lon'], locs[next-1]['lat'],
                        locs[next]['lon'], locs[next]['lat']) <= group_dist))
    stops = []
    for g in groups:
        deltat = g[-1]['timestamp'] - g[0]['timestamp']
        if deltat >= datetime.timedelta(minutes=min_time):
            stops.append({'lon': median([gv['lon'] for gv in g]),
                          'lat': median([gv['lat'] for gv in g]),
                          'arrival': g[0]['timestamp'],
                          'departure': g[0]['timestamp'] + deltat,
                          'records': list(x for x in g),
                        })
    return stops

def get_antennas(records, group_dist=50, checks=True):
        """
        Takes an (ordered) list of 'records' dictionaries
        with fields 'lat', 'lon', and 'timestamp'.

        Function: (1) Mutates dictionaries by adding 'antenna_id' field.
                  (2) Returns an antenna_id to 'lat', 'lon' mapping

        Returns: 
          antenna_id for each record (list).
          antenna_id to {'lat', 'lon'} dictionary.
        """
        def _run_input_checks(records):
            assert(len(records) > 0)
            for r in records:
                assert('lat' in r)
                assert('lon' in r)
                if 'position' in r:
                    assert(r['position'].antenna is None)
        if checks:
            _run_input_checks(records)

        stops = get_stops(records, 50)

        # convert to points and get the labels.
        points = [[s['lon'], s['lat']] for s in stops]
        labels = dbscan(points, 100, 1)
        assert(len(stops) == len(labels))#Ensure a one-to-one correspondence.

        # Associate the labels with the stops.
        for i in range(len(stops)):
            stops[i]['antenna_id'] = labels[i]

        # For each stop:
        # Associate all its records with the antenna.
        # Group the stops by label.
        antennas = {}
        for stop in stops:
            antenna_id = stop['antenna_id']
            for record in stop['records']:
                _is_same = sum(record is x for x in records)
                assert(_is_same == 1)
                record['antenna_id'] = antenna_id
            antennas[antenna_id] = (median([s['lat'] for s in stop['records']]),
                                    median([s['lon'] for s in stop['records']]))
        all_records = sum(len(stop['records']) for stop in stops)
        assert all_records == len(records), "have "+str(all_records)+" expected "+str(len(records))
        return antennas
