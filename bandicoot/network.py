from __future__ import division

from collections import Counter
from itertools import groupby, combinations
from functools import partial


def _count_interaction(user, interaction=None, direction='out'):
    if interaction is None:
        filtered = [x.correspondent_id for x in user.records if x.direction == direction]
    else:
        filtered = [x.correspondent_id for x in user.records if x.interaction == interaction and x.direction == direction]
    return Counter(filtered)


_count_text = partial(_count_interaction, interaction='text')
_count_call = partial(_count_interaction, interaction='call')


def _count_call_duration(user, direction='out'):
    """
    Returns a dictionary of (id, total duration of calls).
    """
    calls_out = (x for x in user.records if x.interaction == 'call' and x.direction == direction)
    grouped_by_id = groupby(calls_out, lambda r: r.correspondent_id)
    return {key: sum(r.call_duration for r in records) for (key, records) in grouped_by_id}


def __generate_matrix(user, generating_fn, default=0, missing=None):
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

    m = [[m1[i][j] or m2[j][i] for i in range(len(neighbors))] for j in range(len(neighbors))]
    return m


def _interaction_matrix(user, interaction=None):
    return __generate_matrix(user, partial(_count_interaction, interaction=interaction))


_interaction_matrix_call = lambda user: __generate_matrix(user, _count_call)
_interaction_matrix_text = lambda user: __generate_matrix(user, _count_text)
_interaction_matrix_call_duration = lambda user: __generate_matrix(user, _count_call_duration)


def directed_weighted_matrix(user, interaction=None):
    """
    Returns a directed, weighted matrix for call, text and call duration.
    If interaction is None the weight is the sum of the number of calls and texts.
    """
    return _interaction_matrix(user, interaction=interaction)


def directed_unweighted_matrix(user):
    """
    Returns a directed, unweighted matrix where an edge exists if there is at least one call or text.
    """
    matrix = _interaction_matrix(user, interaction=None)
    for a in range(len(matrix)): 
        for b in range(len(matrix)):
            matrix[a][b] = 1 if matrix[a][b] else 0
            matrix[b][a] = 1 if matrix[b][a] else 0

    return matrix


def undirected_weighted_matrix(user, interaction=None):
    """
    Returns an undirected, weighted matrix for call, text and call duration where an edge exists if the relationship is reciprocated.
    """
    matrix = _interaction_matrix(user, interaction=interaction)
    for a in range(len(matrix)): 
        for b in range(len(matrix)):
            if matrix[a][b] and matrix[b][a]:
                matrix[a][b], matrix[b][a] = (matrix[a][b] + matrix[b][a]), (matrix[a][b] + matrix[b][a])
            else:
                matrix[a][b] = 0 if matrix[a][b] != None else None
                matrix[b][a] = 0 if matrix[b][a] != None else None

    return matrix


def undirected_unweighted_matrix(user):
    """
    Returns an undirected, unweighted matrix where an edge exists if the relationship is reciprocated.
    """
    matrix = _interaction_matrix(user, interaction=None)
    for a, b in combinations(range(len(matrix)), 2):
        if matrix[a][b] and matrix[b][a]:
            matrix[a][b], matrix[b][a] = 1, 1
        else:
            matrix[a][b] = 0 if matrix[a][b] != None else None
            matrix[b][a] = 0 if matrix[b][a] != None else None

    return matrix


def unweighted_clustering_coefficient(user):
    """
    The clustering coefficient of ego in the user's unweighted, undirected network.
    """
    matrix = undirected_unweighted_matrix(user)
    triplets, closed_triplets = 0, 0
    for a, b, c in combinations(range(len(matrix)), 3):
        triplets += 1. if matrix[a][b] and matrix[a][c] else 0
        closed_triplets += 1. if matrix[a][b] and matrix[a][c] and matrix[b][c] else 0

    return closed_triplets / triplets if triplets != 0 else 0


def weighted_clustering_coefficient(user, interaction=None):
    """
    The clustering coefficient of ego in the user's weighted, undirected network.
    """
    matrix = undirected_weighted_matrix(user, interaction=interaction)
    triplet_weight, degree = 0, 0
    max_weight = max(sum(matrix,[]))
    for a, b, c in combinations(range(len(matrix)), 3):
        degree += 1. if matrix[a][b] else 0
        triplet_weight += (matrix[a][b] * matrix[a][c] * matrix[b][c] / (max_weight ** 3)) ** 1./3 if matrix[a][b] and matrix[a][c] and matrix[b][c] else 0

    return triplet_weight / (degree * (degree - 1)) if degree > 1 else 0
    