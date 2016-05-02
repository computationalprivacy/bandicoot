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

from collections import Counter, defaultdict
from itertools import groupby, combinations
from functools import partial
from datetime import datetime, timedelta
from bandicoot.utils import all
import bandicoot as bc

import os
import random


def _round_half_hour(record):
    """
    Round a time DOWN to half nearest half-hour.
    """
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
        filtered = [x.correspondent_id for x in user.records if
                    x.interaction == interaction and x.direction == direction]
    else:
        raise ValueError("{} is not a correct value of interaction, only 'call'"
                         ", 'text', and 'call_duration' are accepted".format(interaction))
    return Counter(filtered)


def _interaction_matrix(user, interaction=None, default=0, missing=None):
    generating_fn = partial(_count_interaction, interaction=interaction)

    # Just in case, we remove the user from user.network (self records can happen)
    neighbors = matrix_index(user)

    def make_direction(direction):
        rows = []
        for u in neighbors:
            correspondent = user.network.get(u, user)

            if correspondent is None:
                # We assume that missing users don't interact with themselves
                row = [missing if v != u else 0 for v in neighbors]
            else:
                cur_out = generating_fn(correspondent, direction=direction)
                row = [cur_out.get(v, default) for v in neighbors]
            rows.append(row)
        return rows

    m1 = make_direction('out')
    m2 = make_direction('in')

    m = [[m1[i][j] if m1[i][j] is not None else m2[j][i]
         for j in range(len(neighbors))] for i in range(len(neighbors))]
    return m


def matrix_index(user):
    """
    Returns the keys associated with each axis of the matrices.

    The first key is always the name of the current user, followed by the
    sorted names of all the correspondants.
    """

    other_keys = sorted([k for k in user.network.keys() if k != user.name])
    return [user.name] + other_keys


def matrix_directed_weighted(user, interaction=None):
    """
    Returns a directed, weighted matrix for call, text and call duration.

    If interaction is None, the weight measures both calls and texts: the
    weight is the number of 30 minutes periods with at least one call or
    one text.

    Examples
    --------

    >>> m = bc.network.matrix_directed_weighted(user, interaction='call')

    ``m[i][j]`` is the number of calls from ``i`` to ``j``.
    """
    return _interaction_matrix(user, interaction=interaction)


def matrix_directed_unweighted(user):
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


def matrix_undirected_weighted(user, interaction=None):
    """
    Returns an undirected, weighted matrix for call, text and call duration
    where an edge exists if the relationship is reciprocated.
    """
    matrix = _interaction_matrix(user, interaction=interaction)
    result = [[0 for _ in range(len(matrix))] for _ in range(len(matrix))]

    for a in range(len(matrix)):
        for b in range(len(matrix)):
            if a != b and matrix[a][b] and matrix[b][a]:
                result[a][b] = matrix[a][b] + matrix[b][a]
            elif matrix[a][b] is None or matrix[b][a] is None:
                result[a][b] = None
            else:
                result[a][b] = 0

    return result


def matrix_undirected_unweighted(user):
    """
    Returns an undirected, unweighted matrix where an edge exists if the
    relationship is reciprocated.
    """
    matrix = matrix_undirected_weighted(user, interaction=None)
    for a, b in combinations(range(len(matrix)), 2):
        if matrix[a][b] is None or matrix[b][a] is None:
            continue

        if matrix[a][b] > 0 and matrix[b][a] > 0:
            matrix[a][b], matrix[b][a] = 1, 1

    return matrix


def clustering_coefficient_unweighted(user):
    """
    The clustering coefficient of the user in the unweighted, undirected ego
    network.

    It is defined by counting the number of closed triplets including
    the current user:

    .. math::
        C = \\frac{2 * \\text{closed triplets}}{ \\text{degree} \, (\\text{degree - 1})}

    where ``degree`` is the degree of the current user in the network.
    """
    matrix = matrix_undirected_unweighted(user)
    closed_triplets = 0

    for a, b in combinations(range(len(matrix)), 2):
        a_b, a_c, b_c = matrix[a][b], matrix[a][0], matrix[b][0]

        if a_b is None or a_c is None or b_c is None:
            continue

        if a_b > 0 and a_c > 0 and b_c > 0:
            closed_triplets += 1.

    d_ego = sum(matrix[0])
    return 2 * closed_triplets / (d_ego * (d_ego - 1)) if d_ego > 1 else 0


def clustering_coefficient_weighted(user, interaction=None):
    """
    The clustering coefficient of the user's weighted, undirected network.

    It is defined the same way as :meth`~bandicoot.network.clustering_coefficient_unweighted`,
    except that closed triplets are weighted by the number of interactions. For
    each triplet (A, B, C), we compute the geometric mean of the number of
    interactions, using the undirected weighted matrix:

    .. math::
        weight_{abc} = (m_{ab} \; m_{bc} \; m_{ac})^{1/3}

    The weight is normalized, between 0 and 1, by the maximum value in the
    matrix.
    """
    matrix = matrix_undirected_weighted(user, interaction=interaction)
    weights = [weight for g in matrix for weight in g if weight is not None]

    if len(weights) == 0:
        return None
    max_weight = max(weights)
    triplet_weight = 0

    for a, b in combinations(range(len(matrix)), 2):
        a_b, a_c, b_c = matrix[a][b], matrix[a][0], matrix[b][0]

        if a_b is None or a_c is None or b_c is None:
            continue

        if a_b and a_c and b_c:
            triplet_weight += (a_b * a_c * b_c) ** (1 / 3) / max_weight

    d_ego = sum(1 for i in matrix[0] if i > 0)
    return 2 * triplet_weight / (d_ego * (d_ego - 1)) if d_ego > 1 else 0


def assortativity_indicators(user):
    """
    Computes the assortativity of indicators.

    This indicator measures the similarity of the current user with his
    correspondants, for all bandicoot indicators. For each one, it calculates
    the variance of the current user's value with the values for all his
    correspondants:

    .. math::

        \\text{assortativity}(J) = \\frac{1}{n} \\sum_i^n (J_{\\text{user}} - J_{\\text{i}})^2

    for the indicator :math:`J`, and all the :math:`n` correspondents.
    """

    matrix = matrix_undirected_unweighted(user)

    count_indicator = defaultdict(int)
    total_indicator = defaultdict(int)

    # Use all indicator except reporting variables and attributes
    ego_indics = all(user, flatten=True)
    ego_indics = {a: value for a, value in ego_indics.items()
                  if a != "name" and a[:11] != "reporting__" and
                  a[:10] != "attributes"}

    for i, u_name in enumerate(matrix_index(user)):
        correspondent = user.network.get(u_name, None)
        if correspondent is None or u_name == user.name or matrix[0][i] == 0:  # Non reciprocated edge
            continue

        neighbor_indics = all(correspondent, flatten=True)
        for a in ego_indics:
            if ego_indics[a] is not None and neighbor_indics[a] is not None:
                total_indicator[a] += 1
                count_indicator[a] += (ego_indics[a] - neighbor_indics[a]) ** 2

    assortativity = {}
    for i in count_indicator:
        assortativity[i] = count_indicator[i] / total_indicator[i]

    return assortativity


def assortativity_attributes(user):
    """
    Computes the assortativity of the nominal attributes.

    This indicator measures the homophily of the current user with his
    correspondants, for each attributes. It returns a value between 0
    (no assortativity) and 1 (all the contacts share the same value):
    the percentage of contacts sharing the same value.
    """

    matrix = matrix_undirected_unweighted(user)

    neighbors = [k for k in user.network.keys() if k != user.name]
    neighbors_attrbs = {}
    for i, u_name in enumerate(matrix_index(user)):
        correspondent = user.network.get(u_name, None)
        if correspondent is None or u_name == user.name or matrix[0][i] == 0:
            continue

        if correspondent.has_attributes:
            neighbors_attrbs[correspondent.name] = correspondent.attributes

    assortativity = {}
    for a in user.attributes:
        total = sum(1 for n in neighbors if n in neighbors_attrbs and user.attributes[a] == neighbors_attrbs[n][a])
        den = sum(1 for n in neighbors if n in neighbors_attrbs)
        assortativity[a] = total / den if den != 0 else None

    return assortativity


def network_sampling(n, filename, directory=None, snowball=False, user=None):
    """
    Selects a few users and exports a CSV of indicators for them.

    TODO: Returns the network/graph between the selected users.

    Parameters
    ----------
    n : int
        Number of users to select.
    filename : string
        File to export to.
    directory: string
        Directory to select users from if using the default random selection.

    Selection options
    -----------------
    random (default): selects n users at random

    snowball: starts from a specified user, iterates over neighbors, and does a BFS until n neighbors are reached
    """
    if snowball:
        if user is None:
            raise ValueError("Must specify a starting user from whom to initiate the snowball")
        else:
            users, agenda = [user], [user]
            while len(agenda) > 0:
                parent = agenda.pop()
                dealphebetized_network = sorted(parent.network.items(), key=lambda k: random.random())
                for neighbor in dealphebetized_network:
                    if neighbor[1] not in users and neighbor[1] is not None and len(users) < n:
                        users.append(neighbor[1])
                        if neighbor[1].network:
                            agenda.push(neighbor[1])
    else:
        files = [x for x in os.listdir(directory) if os.path.isfile(os.path.join(directory, x))]
        shuffled_files = sorted(files, key=lambda k: random.random())
        user_names = shuffled_files[:n]
        users = [bc.read_csv(u[:-4], directory) for u in user_names]
    if len(users) < n:
        raise ValueError("Specified more users than records that exist, only {} records available".format(len(users)))

    bc.to_csv([bc.utils.all(u) for u in users], filename)
