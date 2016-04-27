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

from .helper.group import recharges_grouping
from .helper.maths import summary_stats
from .helper.tools import pairwise


@recharges_grouping
def amount_recharges(recharges):
    """
    Returns the distribution of amount recharged on the mobile phone.
    """
    return summary_stats([r.amount for r in recharges])


@recharges_grouping
def interevent_time_recharges(recharges):
    """
    Return the distribution of time between consecutive recharges
    of the user.
    """
    time_pairs = pairwise(r.datetime for r in recharges)
    times = [(new - old).total_seconds() for old, new in time_pairs]
    return summary_stats(times)


@recharges_grouping
def percent_pareto_recharges(recharges, percentage=0.8):
    """
    Percentage of recharges that account for 80% of total recharged amount.
    """
    amounts = sorted([r.amount for r in recharges], reverse=True)
    total_sum = sum(amounts)
    partial_sum = 0

    for count, a in enumerate(amounts):
        partial_sum += a
        if partial_sum >= percentage * total_sum:
            break

    return (count + 1) / len(recharges)


@recharges_grouping
def number_of_recharges(recharges):
    """
    Total number of recharges
    """
    return len(recharges)


def average_balance_recharges(user, **kwargs):
    """
    Return the average daily balance estimated from all recharges. We assume a
    linear usage between two recharges, and an empty balance before a recharge.

    The average balance can be seen as the area under the curve delimited by
    all recharges.
    """

    balance = 0
    for r1, r2 in pairwise(user.recharges):
        balance += r1.amount * (r2.datetime - r1.datetime).days / 2

    first_recharge = user.recharges[0]
    last_recharge = user.recharges[-1]
    return balance / (last_recharge.datetime - first_recharge.datetime).days
