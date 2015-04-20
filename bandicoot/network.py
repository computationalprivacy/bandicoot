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


def clustering_coefficient(user, interaction=None, weighted=False):
    """
    The clustering coefficient of the user's ego undirected network.
    """

    matrix = _interaction_matrix(user, interaction=interaction)

    connected_triplets, triplets = 0, 0
    for a, b, c in combinations(range(len(matrix)), 3):
        if matrix[a][b] and matrix[b][c] and matrix[a][c]:
            if weighted:
                triplets += (matrix[a][b] * matrix[b][c]) ** .5
            elif not weighted:
                triplets += 1

            if matrix[a][b] != 0 and matrix[b][c] != 0 and matrix[a][c] != 0:
                if weighted:
                    connected_triplets += (matrix[a][b] * matrix[b][c]) ** .5
                else:
                    connected_triplets += 1

    return float(connected_triplets) / triplets if triplets != 0 else 0
    