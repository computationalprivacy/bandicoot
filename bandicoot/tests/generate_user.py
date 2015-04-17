#!/usr/bin/python

import hashlib
import datetime
import random
import math
import csv
import copy

from bandicoot.core import Record, Position
import bandicoot as bc
from bandicoot.helper.tools import OrderedDict


def random_record(**kwargs):
    n_users = 48
    rate = 1e-4

    year  = 2012
    month = random.choice(range(1, 3))
    day   = random.choice(range(1, 28))
    
    # ensures that some correspondents have more interactions than others
    correspondent = random.randint(0, n_users/2)+random.randint(0, n_users/2)

    r = {'datetime': datetime.datetime(year, month, day) + datetime.timedelta(seconds=math.floor(-1/rate*math.log(random.random()))),
         'interaction':  random.choice(['text', 'text', 'text', 'call', 'call']),
         'correspondent_id': "correspondent_{}".format(correspondent),
         'direction': random.choice(['in', 'in', 'out']),
         'call_duration': random.randint(1, 1000),
         'position': Position(location=(random.uniform(-5, 5), random.uniform(-5, 5)))}
    if r['interaction'] == "text":
        r['call_duration'] = None

    r.update(kwargs)
    return Record(**r)


def sample_user(number_records=1482, seed=42, pct_in_network=0.8):
    old_state = random.getstate()
    random.seed(seed)

    towers = {701:(42.3555,-71.099541),
        702:(42.359039,-71.094595),
        703:(42.360481,-71.087321),
        704:(42.361013,-71.097868),
        705:(42.370849,-71.114613),
        706:(42.3667427,-71.1069847),
        707:(42.367589,-71.076537)}
    towers_position = [Position(antenna=k, location=v) for k, v in towers.items()]

    ego_records = [random_record(position=random.choice(towers_position)) for _ in xrange(number_records)]
    user = bc.io.load("sample_user", ego_records, towers, None, describe=False)
    
    # create network
    correspondents = set([record.correspondent_id for record in ego_records])
    between_user_records = {}
    correspondent_records = {}
    connections = {}
    
    n_in_network     = int(len(correspondents)*pct_in_network)
    if (n_in_network % 2 != 0):
        n_in_network = n_in_network - 1     
    in_network_correspondents = random.sample(correspondents, n_in_network)
    
    def reverse_records(records, current_owner):
        for r in records:
            r.direction = 'out' if r.direction == 'in' else 'in'  
            r.correspondent_id = current_owner
        return records
            
    # set records from ego
    for c_id in sorted(in_network_correspondents):
        reciprocal_records = filter(lambda r: r.correspondent_id == c_id, ego_records)
        reciprocal_records = reverse_records(copy.deepcopy(reciprocal_records), "ego")
        correspondent_records[c_id]  = reciprocal_records
    
    def generate_group_with_random_links(pct_users_in_group):
        n_in_group                  = int(len(correspondents)*pct_users_in_group)
        group                       = random.sample(non_grouped_correspondents, n_in_group)
        networkusers_group          = list()
        for user in group:
            if user in in_network_correspondents:
                networkusers_group.append(user)

        def CreatePair(source):        
            user_pair = [source, random.sample(group, 1)[0]]
            if user_pair[0] in non_grouped_correspondents:
                non_grouped_correspondents.remove(user_pair[0])
            if user_pair[1] in non_grouped_correspondents:
                non_grouped_correspondents.remove(user_pair[1])            
        
            extra_records = [random_record(position=random.choice(towers_position), interaction=random.choice(['text', 'call', 'call']), correspondent_id=user_pair[1]) for _ in xrange(random.randrange(25,150))]
            correspondent_records[user_pair[0]].extend(extra_records)
            if (user_pair[1] in in_network_correspondents):
                correspondent_records[user_pair[1]].extend(reverse_records(copy.deepcopy(extra_records), user_pair[0]))        
        
        # create pairs of users
        for i in range(len(networkusers_group)):
            CreatePair(networkusers_group[i])
            if random.choice(range(2)) == 0:
                CreatePair(networkusers_group[i])


    non_grouped_correspondents = copy.deepcopy(correspondents)
    for i in range(4):
        generate_group_with_random_links(pct_users_in_group=0.4-i*0.1)
        
    # create user object
    for c_id in sorted(correspondents):
        if (c_id in in_network_correspondents):
            correspondent_user =  bc.io.load(c_id, correspondent_records[c_id], towers, None, describe=False)
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

    schema = ['interaction', 'direction', 'correspondent_id', 'datetime', 'call_duration', 'antenna_id']
    with open(filepath, "wb") as new_user:
        w = csv.writer(new_user)
        w.writerow(schema)

        for record in user.records:
            w.writerow([record.position.antenna if x == 'antenna_id' else getattr(record, x) for x in schema])

    print "Finished writing new user to " + filepath
    write_answers(user)

def write_answers(user):
    bc.io.to_json([bc.utils.all(user, groupby='week', summary='default')], "samples/automatic/automatic_result.json")
    bc.io.to_json([bc.utils.all(user, groupby='week', summary='extended')], "samples/automatic/automatic_result_extended.json")
    bc.io.to_json([bc.utils.all(user, groupby=None, summary='default')], "samples/automatic/automatic_result_no_grouping.json")


def random_burst(count, delta=datetime.timedelta(minutes=10), **kwargs):

    first_date = datetime.datetime(2014, 01, 01, 10, 41)

    for i in range(count):
        _date = first_date + delta * i
        yield random_record(datetime=_date, **kwargs)


def random_records(n, antennas, number_of_users=150, ingoing=0.7, percent_text=0.3, rate=1e-4):
    current_date = datetime.datetime(2013, 01, 01, 00, 00, 00)
    results = []

    for _ in range(n):
        current_date += datetime.timedelta(seconds=math.floor(-1/rate*math.log(random.random())))
        interaction = "text" if random.random() < percent_text else "call"
        r = Record(
            interaction=interaction,
            direction='in' if random.random() < ingoing else 'out',
            correspondent_id=hashlib.md5(str(random.randint(1, number_of_users))).hexdigest(),
            datetime=str(current_date),
            call_duration=random.randint(1, 1000) if interaction == "call" else '',
            position=random.choice(antennas)
        )
        results.append(r._asdict())

    return results
