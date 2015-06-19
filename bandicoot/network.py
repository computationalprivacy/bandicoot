from __future__ import division

from collections import Counter, defaultdict
from itertools import groupby, combinations
from functools import partial
from datetime import datetime, timedelta
from bandicoot.utils import all, OrderedDict


def _round_half_hour(record):
    k = record.datetime + timedelta(minutes=-(record.datetime.minute % 30))
    return datetime(k.year, k.month, k.day, k.hour, k.minute, 0)


def _count_interaction(user, interaction=None, direction='out'):
    if interaction is 'call_duration':
        d = defaultdict(int)
        for r in user.records:
            if r.direction == direction and r.interaction == 'call':
                d[r.correspondent_id] += r.call_duration
        return d

    if interaction is None:
        keyfn = lambda x: x.correspondent_id
        records = (r for r in user.records if r.direction == direction)
        chunks = groupby(sorted(records, key=keyfn), key=keyfn)
        # Count the number of distinct half-hour blocks for each user
        return Counter({c_id: len(set((_round_half_hour(i) for i in items))) for c_id, items in chunks})

    if interaction in ['call', 'text']:
        filtered = [x.correspondent_id for x in user.records if x.interaction == interaction and x.direction == direction]
    else:
        raise ValueError("{} is not a correct value of interaction, only 'call'"
                         ", 'text', and 'call_duration' are accepted".format(interaction))
    return Counter(filtered)


def _interaction_matrix(user, interaction=None, default=0, missing=None):
    generating_fn = partial(_count_interaction, interaction=interaction)

    # Just in case, we remove the user from user.network (self records can happen)
    neighbors = [user.name] + sorted([k for k in user.network.keys() if k != user.name])

    def make_direction(direction):
        rows = []
        for u in neighbors:
            correspondent = user.network.get(u, user)

            if correspondent is None:
                row = [missing for v in neighbors]
            else:
                cur_out = generating_fn(correspondent, direction=direction)
                row = [cur_out.get(v, default) for v in neighbors]
            rows.append(row)
        return rows

    m1 = make_direction('out')
    m2 = make_direction('in')

    m = [[m1[i][j] if m1[i][j] is not None else m2[j][i] for i in range(len(neighbors))] for j in range(len(neighbors))]
    return m


def directed_weighted_matrix(user, interaction=None):
    """
    Returns a directed, weighted matrix for call, text and call duration.
    If interaction is None the weight is the sum of the number of calls and texts.
    """
    return _interaction_matrix(user, interaction=interaction)


def directed_unweighted_matrix(user):
    """
    Returns a directed, unweighted matrix where an edge exists if there is at
    least one call or text.
    """
    matrix = _interaction_matrix(user, interaction=None)
    for a in range(len(matrix)):
        for b in range(len(matrix)):
            if matrix[a][b] is not None and matrix[a][b] > 0:
                matrix[a][b] = 1

    return matrix


def undirected_weighted_matrix(user, interaction=None):
    """
    Returns an undirected, weighted matrix for call, text and call duration
    where an edge exists if the relationship is reciprocated.
    """
    matrix = _interaction_matrix(user, interaction=interaction)
    result = [[0 for _ in range(len(matrix))] for _ in range(len(matrix))]

    for a in range(len(matrix)):
        for b in range(len(matrix)):
            if a != b and matrix[a][b] and matrix[b][a] and matrix[a][b] + matrix[b][a] > 0:
                result[a][b] = matrix[a][b] + matrix[b][a]
            elif matrix[a][b] is None or matrix[b][a] is None:
                result[a][b] = None
            else:
                result[a][b] = 0

    return result


def undirected_unweighted_matrix(user):
    """
    Returns an undirected, unweighted matrix where an edge exists if the
    relationship is reciprocated.
    """
    matrix = undirected_weighted_matrix(user, interaction=None)
    for a, b in combinations(range(len(matrix)), 2):
        if matrix[a][b] > 0 and matrix[b][a] > 0:
            matrix[a][b], matrix[b][a] = 1, 1

    return matrix


def unweighted_clustering_coefficient(user):
    """
    The clustering coefficient of the user in the unweighted, undirected ego
    network.
    """
    matrix = undirected_unweighted_matrix(user)
    closed_triplets = 0

    for a, b in combinations(xrange(len(matrix)), 2):
        a_b, a_c, b_c = matrix[a][b], matrix[a][0], matrix[b][0]

        if a_b is not None and a_c is not None and b_c is not None:
            if a_b > 0 and a_c > 0 and b_c > 0:
                closed_triplets += 1.

    d_ego = sum(matrix[0])
    return 2 * closed_triplets / (d_ego * (d_ego - 1)) if d_ego > 1 else 0


def weighted_clustering_coefficient(user, interaction=None):
    """
    The clustering coefficient of the user's weighted, undirected network.
    """
    matrix = undirected_weighted_matrix(user, interaction=interaction)
    triplet_weight = 0
    max_weight = max(weight for g in matrix for weight in g)

    for a, b in combinations(range(len(matrix)), 2):
        a_b, a_c, b_c = matrix[a][b], matrix[a][0], matrix[b][0]

        if a_b is not None and a_c is not None and b_c is not None:
            if a_b and a_c and b_c:
                triplet_weight += (a_b * a_c * b_c ) ** (1/3) / max_weight

    d_ego = sum(1 for i in matrix[0] if i > 0)
    return 2 * triplet_weight / (d_ego * (d_ego - 1)) if d_ego > 1 else 0


def indicators_assortativity(user):
    """
    Computes the assortativity of indicators.
    """
    assortativity = OrderedDict()
    ego_indics = all(user, flatten=True)
    for a in ego_indics:
        if a != "name" and a[:11] != "reporting__" and a[:10] != "attributes":
            assortativity[a] = [None,0]
    neighbors = [k for k in user.network.keys() if k != user.name]
    for u in neighbors:
        correspondent = user.network.get(u, user)
        if correspondent is not None:
            neighbor_indics = all(correspondent, flatten=True)
            for a in assortativity:
                if ego_indics[a] is not None and neighbor_indics[a] is not None:
                    assortativity[a][1] += 1
                    if assortativity[a][0] is None:
                        assortativity[a][0] = 0
                    assortativity[a][0] += (ego_indics[a] - neighbor_indics[a]) ** 2
    for i in assortativity:
        if assortativity[i][0] is not None:
            assortativity[i] = assortativity[i][0] / assortativity[i][1]
        else:
            assortativity[i] is None

    return assortativity


def attributes_assortativity(user):
    """
    Computes the assortativity of the nominal attributes.
    """
    assortativity = {}
    neighbors = [k for k in user.network.keys() if k != user.name]
    neighbors_attrbs = {}
    for u in neighbors:
        correspondent = user.network.get(u,user)
        if correspondent is not None and correspondent.has_attributes:
            neighbors_attrbs[u] = correspondent.attributes
    for a in user.attributes:
        total = sum(1 for n in neighbors if n in neighbors_attrbs and user.attributes[a] == neighbors_attrbs[n][a])
        den = sum(1 for n in neighbors if n in neighbors_attrbs)
        assortativity[a] = total / den

    return assortativity
