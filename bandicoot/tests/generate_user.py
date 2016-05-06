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

import datetime
import random
import math
import csv
import copy

from bandicoot.core import Record, Position
import bandicoot as bc
from bandicoot.helper.tools import OrderedDict


def _choice(seq):
    return seq[int(random.random() * len(seq))]


def _uniform(a, b):
    return a + (b - a) * random.random()


def _randint(a, b):
    return int(_uniform(a, b))


def _sample(population, k):
    n = len(population)
    result = [None] * k

    selected = set()
    selected_add = selected.add
    for i in range(k):
        j = _randint(0, n)
        while j in selected:
            j = _randint(0, n)
        selected_add(j)
        result[i] = population[j]
    return result


def random_record(**kwargs):
    n_users = 48
    rate = 1e-4

    year = 2012
    month = _choice(range(1, 3))
    day = _choice(range(1, 28))

    # ensures that some correspondents have more interactions than others
    correspondent = int(random.random() * n_users)

    r = {'datetime': datetime.datetime(year, month, day) + datetime.timedelta(seconds=math.floor(-1 / rate * math.log(random.random()))),
         'interaction': _choice(['text', 'text', 'text', 'call', 'call']),
         'correspondent_id': "correspondent_{}".format(correspondent),
         'direction': _choice(['in', 'in', 'out']),
         'call_duration': int(random.random() * 1000),
         'position': Position(location=(_uniform(-5, 5), _uniform(-5, 5)))}
    if r['interaction'] == "text":
        r['call_duration'] = None

    r.update(kwargs)
    return Record(**r)


def sample_user(number_records=1482, seed=42, pct_in_network=0.8):
    old_state = random.getstate()

    try:
        random.seed(seed, version=1)
    except TypeError:
        random.seed(seed)

    towers = {
        701: (42.3555, -71.099541),
        702: (42.359039, -71.094595),
        703: (42.360481, -71.087321),
        704: (42.361013, -71.097868),
        705: (42.370849, -71.114613),
        706: (42.3667427, -71.1069847),
        707: (42.367589, -71.076537)
    }
    towers_position = [Position(antenna=k, location=v)
                       for k, v in towers.items()]

    ego_records = [random_record(
        position=_choice(towers_position)) for _ in range(number_records)]
    user, _ = bc.io.load(
        "sample_user", ego_records, towers, None, describe=False)

    # create network
    correspondents = set([record.correspondent_id for record in ego_records])
    correspondents = sorted(list(correspondents))
    correspondent_records = {}
    connections = {}

    n_in_network = int(len(correspondents) * pct_in_network)
    n_in_network = (n_in_network // 2) * 2
    in_network_correspondents = _sample(correspondents, n_in_network)

    def reverse_records(records, current_owner):
        for r in records:
            r.direction = 'out' if r.direction == 'in' else 'in'
            r.correspondent_id = current_owner
        return records

    # set records from ego
    for c_id in sorted(in_network_correspondents):
        reciprocal_records = [
            r for r in ego_records if r.correspondent_id == c_id]
        reciprocal_records = reverse_records(
            copy.deepcopy(reciprocal_records), "sample_user")
        correspondent_records[c_id] = reciprocal_records

    def generate_group_with_random_links(pct_users_in_group):
        n_in_group = int(len(correspondents) * pct_users_in_group)
        group = _sample(non_grouped_correspondents, n_in_group)
        networkusers_group = list()
        for user in group:
            if user in in_network_correspondents:
                networkusers_group.append(user)

        def create_pair(source):
            user_pair = [source, _choice(group)]
            if user_pair[0] in non_grouped_correspondents:
                non_grouped_correspondents.remove(user_pair[0])
            if user_pair[1] in non_grouped_correspondents:
                non_grouped_correspondents.remove(user_pair[1])

            extra_records = [
                random_record(position=_choice(towers_position),
                              interaction=_choice(['text', 'call', 'call']),
                              correspondent_id=user_pair[1])
                for _ in range(_randint(25, 150))]

            correspondent_records[user_pair[0]].extend(extra_records)
            if (user_pair[1] in in_network_correspondents):
                rr = reverse_records(copy.deepcopy(extra_records), user_pair[0])
                correspondent_records[user_pair[1]].extend(rr)

        # create pairs of users
        for i in range(len(networkusers_group)):
            create_pair(networkusers_group[i])
            if random.random() > 0.5:
                create_pair(networkusers_group[i])

    non_grouped_correspondents = copy.deepcopy(correspondents)
    for i in range(4):
        generate_group_with_random_links(pct_users_in_group=0.4 - i * 0.1)

    # create user object
    for c_id in sorted(correspondents):
        if c_id in in_network_correspondents:
            correspondent_user, _ = bc.io.load(
                c_id, correspondent_records[c_id], towers, None, describe=False)
        else:
            correspondent_user = None
        connections[c_id] = correspondent_user

    # return the network dictionary sorted by key
    user.network = OrderedDict(sorted(connections.items(), key=lambda t: t[0]))
    user.recompute_missing_neighbors()

    random.setstate(old_state)
    return user


def write_new_user(filepath, n=1960):
    user = sample_user(n)

    schema = ['interaction', 'direction', 'correspondent_id',
              'datetime', 'call_duration', 'antenna_id']
    with open(filepath, "wb") as new_user:
        w = csv.writer(new_user)
        w.writerow(schema)

        for record in user.records:
            w.writerow([record.position.antenna if x ==
                        'antenna_id' else getattr(record, x) for x in schema])

    print("Finished writing new user to " + filepath)
    write_answers(user)


def write_answers(user):
    bc.io.to_json([bc.utils.all(user, groupby='week', summary='default')],
                  "samples/automatic/automatic_result.json")
    bc.io.to_json([bc.utils.all(user, groupby='week', summary='extended')],
                  "samples/automatic/automatic_result_extended.json")
    bc.io.to_json([bc.utils.all(user, groupby=None, summary='default')],
                  "samples/automatic/automatic_result_no_grouping.json")


def random_burst(count, delta=datetime.timedelta(minutes=10), **kwargs):

    first_date = datetime.datetime(2014, 1, 1, 10, 41)

    for i in range(count):
        _date = first_date + delta * i
        yield random_record(datetime=_date, **kwargs)
