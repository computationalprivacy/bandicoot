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

from .helper.group import grouping
from .helper.maths import entropy, summary_stats
from .helper.tools import pairwise
from collections import Counter

import math
import datetime
from collections import defaultdict


@grouping
def interevent_time(records):
    """
    The interevent time between two records of the user.
    """
    inter_events = pairwise(r.datetime for r in records)
    inter = [(new - old).total_seconds() for old, new in inter_events]

    return summary_stats(inter)


@grouping
def number_of_contacts(records, direction=None, more=0):
    """
    The number of contacts the user interacted with.

    Parameters
    ----------
    direction : str, optional
        Filters the records by their direction: ``None`` for all records,
        ``'in'`` for incoming, and ``'out'`` for outgoing.
    more : int, default is 0
        Counts only contacts with more than this number of interactions.
    """
    if direction is None:
        counter = Counter(r.correspondent_id for r in records)
    else:
        counter = Counter(r.correspondent_id for r in records if r.direction == direction)
    return sum(1 for d in counter.values() if d > more)


@grouping
def entropy_of_contacts(records, normalize=False):
    """
    The entropy of the user's contacts.

    Parameters
    ----------
    normalize: boolean, default is False
        Returns a normalized entropy between 0 and 1.

    """
    counter = Counter(r.correspondent_id for r in records)

    raw_entropy = entropy(counter.values())
    n = len(counter)
    if normalize and n > 1:
        return raw_entropy / math.log(n)
    else:
        return raw_entropy


@grouping
def interactions_per_contact(records, direction=None):
    """
    The number of interactions a user had with each of its contacts.

    Parameters
    ----------
    direction : str, optional
        Filters the records by their direction: ``None`` for all records,
        ``'in'`` for incoming, and ``'out'`` for outgoing.
    """
    if direction is None:
        counter = Counter(r.correspondent_id for r in records)
    else:
        counter = Counter(r.correspondent_id for r in records
                          if r.direction == direction)
    return summary_stats(counter.values())


@grouping(user_kwd=True, interaction='call')
def percent_initiated_interactions(records, user):
    """
    The percentage of calls initiated by the user.
    """
    if len(records) == 0:
        return 0

    initiated = sum(1 for r in records if r.direction == 'out')
    return initiated / len(records)


@grouping(user_kwd=True)
def percent_nocturnal(records, user):
    """
    The percentage of interactions the user had at night.

    By default, nights are 7pm-7am. Nightimes can be set in
    ``User.night_start`` and ``User.night_end``.
    """
    if len(records) == 0:
        return 0

    if user.night_start < user.night_end:
        night_filter = lambda d: user.night_end > d.time() > user.night_start
    else:
        night_filter = lambda d: not(user.night_end < d.time() < user.night_start)

    return sum(1 for r in records if night_filter(r.datetime)) / len(records)


@grouping(interaction='call')
def call_duration(records, direction=None):
    """
    The duration of the user's calls.

    Parameters
    ----------
    direction : str, optional
        Filters the records by their direction: ``None`` for all records,
        ``'in'`` for incoming, and ``'out'`` for outgoing.
    """
    if direction is None:
        call_durations = [r.call_duration for r in records]
    else:
        call_durations = [r.call_duration for r in records if r.direction == direction]

    return summary_stats(call_durations)


def _conversations(group, delta=datetime.timedelta(hours=1)):
    """
    Group texts into conversations. The function returns an iterator over records grouped by conversations.

    See :ref:`Using bandicoot <conversations-label>` for a definition of conversations.

    A conversation begins when one person sends a text-message to the other and ends when one of them makes a phone call
    or there is no activity between them for an hour.
    """
    last_time = None
    results = []
    for g in group:

        if last_time is None or g.datetime - last_time < delta:
            if g.interaction == 'text':
                results.append(g)

            # A call always ends a conversation
            else:
                if len(results) != 0:
                    yield results
                    results = []

        else:
            if len(results) != 0:
                yield results

            if g.interaction == 'call':
                results = []
            else:
                results = [g]

        last_time = g.datetime

    if len(results) != 0:
        yield results


@grouping(interaction='callandtext')
def response_rate_text(records):
    """
    The response rate of the user (between 0 and 1).

    Considers text-conversations which began with an incoming text.  Response rate
    is the fraction of such conversations in which the user sent a text (a response).

    The following sequence of messages defines four conversations (``I`` for an
    incoming text, ``O`` for an outgoing text): ::

        I-O-I-O => Started with an incoming text and at least one outgoing text
        I-I-O-I => Started with an incoming text and at least one outgoing text
        I-I-I-I => Started with an incoming text but doesn't have outgoing texts
        O-O-I-O => Not starting with an incoming text

    Here, the ratio would be 2/3 as we have 3 conversations starting with an incoming text and 2 of them have at least one outgoing text.

    See :ref:`Using bandicoot <conversations-label>` for a definition of conversations.
    """
    if len(records) == 0:
        return None

    interactions = defaultdict(list)
    for r in records:
        interactions[r.correspondent_id].append(r)

    def _response_rate(grouped):
        received, responded = 0, 0
        conversations = _conversations(grouped)

        for conv in conversations:
            if len(conv) != 0:
                first = conv[0]
                if first.direction == 'in' and first.interaction == 'text':
                    received += 1
                    if any((i.direction == 'out' for i in conv)):
                        responded += 1

        return responded, received

    # Group all records by their correspondent, and compute the response rate
    # for each
    all_couples = map(_response_rate, list(interactions.values()))
    responded, received = map(sum, list(zip(*all_couples)))

    return responded / received if received != 0 else None


@grouping(interaction='callandtext')
def response_delay_text(records):
    """
    The response delay of the user within a conversation (in seconds)

    The following sequence of messages defines conversations (``I`` for an
    incoming text, ``O`` for an outgoing text, ``-`` for a one minute
    delay): ::

        I-O--I----O, we have a 60 seconds response delay and a 240 seconds response delay
        O--O---I--O, we have a 1200 seconds response delay
        I--II---I-I, we don't have a response delay. The user hasn't answered

    For this user, the distribution of response delays will be ``[60, 240, 60]``

    Notes
    -----
    See :ref:`Using bandicoot <conversations-label>` for a definition of conversations.
    Conversation are defined to be a series of text messages each sent no more than an hour
    after the previous. The response delay can thus not be greater than one hour.
    """
    interactions = defaultdict(list)
    for r in records:
        interactions[r.correspondent_id].append(r)

    def _response_delay(grouped):
        ts = ((b.datetime - a.datetime).total_seconds()
              for conv in _conversations(grouped)
              for a, b in pairwise(conv)
              if b.direction == 'out' and a.direction == 'in')

        return ts

    delays = [r for i in interactions.values() for r in _response_delay(i)
              if r > 0]

    return summary_stats(delays)


@grouping(interaction='callandtext')
def percent_initiated_conversations(records):
    """
    The percentage of conversations that have been initiated by the user.

    Each call and each text conversation is weighted as a single interaction.

    See :ref:`Using bandicoot <conversations-label>` for a definition of
    conversations.
    """
    interactions = defaultdict(list)
    for r in records:
        interactions[r.correspondent_id].append(r)

    def _percent_initiated(grouped):
        mapped = [(1 if conv[0].direction == 'out' else 0, 1)
                  for conv in _conversations(grouped)]
        return mapped

    all_couples = [sublist for i in interactions.values()
                   for sublist in _percent_initiated(i)]

    if len(all_couples) == 0:
        init, total = 0, 0
    else:
        init, total = list(map(sum, list(zip(*all_couples))))

    return init / total if total != 0 else 0


@grouping(interaction='callandtext')
def active_days(records):
    """
    The number of days during which the user was active. A user is considered
    active if he sends a text, receives a text, initiates a call, receives a
    call, or has a mobility point.
    """
    days = set(r.datetime.date() for r in records)
    return len(days)


@grouping
def percent_pareto_interactions(records, percentage=0.8):
    """
    The percentage of user's contacts that account for 80% of its interactions.
    """
    if len(records) == 0:
        return None

    user_count = Counter(r.correspondent_id for r in records)

    target = int(math.ceil(sum(user_count.values()) * percentage))
    user_sort = sorted(user_count.keys(), key=lambda x: user_count[x])

    while target > 0 and len(user_sort) > 0:
        user_id = user_sort.pop()
        target -= user_count[user_id]

    return (len(user_count) - len(user_sort)) / len(records)


@grouping(interaction='call')
def percent_pareto_durations(records, percentage=0.8):
    """
    The percentage of user's contacts that account for 80% of its total time
    spend on the phone. Optionally takes a percentage argument as a decimal
    (e.g., .8 for 80%).
    """
    if len(records) == 0:
        return None

    user_count = defaultdict(int)
    for r in records:
        if r.interaction == "call":
            user_count[r.correspondent_id] += r.call_duration

    target = int(math.ceil(sum(user_count.values()) * percentage))
    user_sort = sorted(user_count.keys(), key=lambda x: user_count[x])

    while target > 0 and len(user_sort) > 0:
        user_id = user_sort.pop()
        target -= user_count[user_id]

    return (len(user_count) - len(user_sort)) / len(records)


@grouping
def balance_of_contacts(records, weighted=True):
    """
    The balance of interactions per contact. For every contact,
    the balance is the number of outgoing interactions divided by the total
    number of interactions (in+out).

    .. math::

       \\forall \\,\\text{contact}\\,c,\\;\\text{balance}\,(c) = \\frac{\\bigl|\\text{outgoing}\,(c)\\bigr|}{\\bigl|\\text{outgoing}\,(c)\\bigr|+\\bigl|\\text{incoming}\,(c)\\bigr|}

    Parameters
    ----------
    weighted : str, optional
        If ``True``, the balance for each contact is weighted by
        the number of interactions the user had with this contact.
    """
    counter_out = defaultdict(int)
    counter = defaultdict(int)

    for r in records:
        if r.direction == 'out':
            counter_out[r.correspondent_id] += 1
        counter[r.correspondent_id] += 1

    if not weighted:
        balance = [counter_out[c] / counter[c] for c in counter]
    else:
        balance = [counter_out[c] / sum(counter.values()) for c in counter]

    return summary_stats(balance)


@grouping()
def number_of_interactions(records, direction=None):
    """
    The number of interactions.

    Parameters
    ----------
    direction : str, optional
        Filters the records by their direction: ``None`` for all records,
        ``'in'`` for incoming, and ``'out'`` for outgoing.
    """
    if direction is None:
        return len(records)
    else:
        return len([r for r in records if r.direction == direction])
