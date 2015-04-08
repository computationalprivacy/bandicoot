#!/usr/bin/python

import hashlib
import datetime
import random
import math
import csv

from bandicoot.core import Record, Position
import bandicoot as bc


def random_record(**kwargs):
    n_users = 150
    rate = 1e-4

    year = random.choice(range(2012, 2015))
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 28))

    r = {'datetime': datetime.datetime(year, month, day) + datetime.timedelta(seconds=math.floor(-1/rate*math.log(random.random()))),
         'interaction': random.choice(['text', 'call']),
         'correspondent_id': random.randint(1, n_users),
         'direction': random.choice(['in', 'out']),
         'call_duration': random.randint(1, 1000),
         'position': Position(location=(random.uniform(-5, 5), random.uniform(-5, 5)))}
    if r['interaction'] == "text":
        r['call_duration'] = ''

    r.update(kwargs)
    return Record(**r)


def sample_user(number_records=1960, seed=42):
    old_state = random.getstate()
    random.seed(42)

    towers = {701:(42.3555,-71.099541),
        702:(42.359039,-71.094595),
        703:(42.360481,-71.087321),
        704:(42.361013,-71.097868),
        705:(42.370849,-71.114613),
        706:(42.3667427,-71.1069847),
        707:(42.367589,-71.076537)}
    towers_position = [Position(antenna=k, location=v) for k, v in towers.items()]

    records = [random_record(position=random.choice(towers_position)) for _ in xrange(number_records)]
    user = bc.io.load("sample_user", records, towers, None)

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
