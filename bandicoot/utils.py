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

from bandicoot.helper.tools import OrderedDict
from bandicoot.helper.group import group_records, group_records_with_padding
from functools import partial

import bandicoot as bc


def flatten(d, parent_key='', separator='__'):
    """
    Flatten a nested dictionary.

    Parameters
    ----------
    d: dict_like
        Dictionary to flatten.
    parent_key: string, optional
        Concatenated names of the parent keys.
    separator: string, optional
        Separator between the names of the each key.
        The default separator is '_'.

    Examples
    --------

    >>> d = {'alpha': 1, 'beta': {'a': 10, 'b': 42}}
    >>> flatten(d) == {'alpha': 1, 'beta_a': 10, 'beta_b': 42}
    True
    >>> flatten(d, separator='.') == {'alpha': 1, 'beta.a': 10, 'beta.b': 42}
    True

    """
    items = []
    for k, v in d.items():
        new_key = parent_key + separator + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    return OrderedDict(items)


def all(user, groupby='week', summary='default', network=False,
        split_week=False, split_day=False, filter_empty=True, attributes=True,
        flatten=False):
    """
    Returns a dictionary containing all bandicoot indicators for the user,
    as well as reporting variables.

    Relevant indicators are defined in the 'individual', and 'spatial' modules.

    =================================== =======================================================================
    Reporting variables                 Description
    =================================== =======================================================================
    antennas_path                       path of the CSV file containing antennas locations
    attributes_path                     directory where attributes were loaded
    version                             bandicoot version
    groupby                             grouping method ('week' or None)
    split_week                          whether or not indicators are also computed for weekday and weekend
    split_day                           whether or not indicators are also computed for day and night
    start_time                          time of the first record
    end_time                            time of the last record
    night_start, night_end              start and end time to define nights
    weekend                             days used to define the weekend (``[6, 7]`` by default, where 1 is Monday)
    bins                                number of weeks if the record are grouped
    has_call                            whether or not records include calls
    has_text                            whether or not records include texts
    has_home                            whether or not a :meth:`home location <bandicoot.core.User.recompute_home>` has been found
    has_network                         whether or not correspondents where loaded
    percent_records_missing_location    percentage of records without location
    antennas_missing_locations          number of antennas missing a location
    percent_outofnetwork_calls          percentage of calls, received or emitted, made with a correspondant not loaded in the network
    percent_outofnetwork_texts          percentage of texts with contacts not loaded in the network
    percent_outofnetwork_contacts       percentage of contacts not loaded in the network
    percent_outofnetwork_call_durations percentage of minutes of calls where the contact was not loaded in the network
    number_of_records                   total number of records
    number_of_weeks                     number of weeks with records
    =================================== =======================================================================

    We also include a last set of reporting variables, for the records ignored
    at load-time. Values can be ignored due to missing or inconsistent fields
    (e.g., not including a valid 'datetime' value).

    .. code-block:: python

        {
            'all': 0,
            'interaction': 0,
            'direction': 0,
            'correspondent_id': 0,
            'datetime': 0,
            'call_duration': 0
        }

    with the total number of records ignored (key ``'all'``), as well as the
    number of records with faulty values for each columns.
    """
    scalar_type = 'distribution_scalar' if groupby is not None else 'scalar'
    summary_type = 'distribution_summarystats' if groupby is not None else 'summarystats'

    number_of_interactions_in = partial(bc.individual.number_of_interactions, direction='in')
    number_of_interactions_in.__name__ = 'number_of_interaction_in'
    number_of_interactions_out = partial(bc.individual.number_of_interactions, direction='out')
    number_of_interactions_out.__name__ = 'number_of_interaction_out'

    functions = [
        (bc.individual.active_days, scalar_type),
        (bc.individual.number_of_contacts, scalar_type),
        (bc.individual.call_duration, summary_type),
        (bc.individual.percent_nocturnal, scalar_type),
        (bc.individual.percent_initiated_conversations, scalar_type),
        (bc.individual.percent_initiated_interactions, scalar_type),
        (bc.individual.response_delay_text, summary_type),
        (bc.individual.response_rate_text, scalar_type),
        (bc.individual.entropy_of_contacts, scalar_type),
        (bc.individual.balance_of_contacts, summary_type),
        (bc.individual.interactions_per_contact, summary_type),
        (bc.individual.interevent_time, summary_type),
        (bc.individual.percent_pareto_interactions, scalar_type),
        (bc.individual.percent_pareto_durations, scalar_type),
        (bc.individual.number_of_interactions, scalar_type),
        (number_of_interactions_in, scalar_type),
        (number_of_interactions_out, scalar_type),
        (bc.spatial.number_of_antennas, scalar_type),
        (bc.spatial.entropy_of_antennas, scalar_type),
        (bc.spatial.percent_at_home, scalar_type),
        (bc.spatial.radius_of_gyration, scalar_type),
        (bc.spatial.frequent_antennas, scalar_type),
        (bc.spatial.churn_rate, scalar_type)
    ]

    if user.has_recharges:
        functions += [
            (bc.recharge.amount_recharges, summary_type),
            (bc.recharge.interevent_time_recharges, summary_type),
            (bc.recharge.percent_pareto_recharges, scalar_type),
            (bc.recharge.number_of_recharges, scalar_type),
            (bc.recharge.average_balance_recharges, scalar_type)
        ]

    network_functions = [
        bc.network.clustering_coefficient_unweighted,
        bc.network.clustering_coefficient_weighted,
        bc.network.assortativity_attributes,
        bc.network.assortativity_indicators
    ]

    groups = list(group_records(user.records, groupby=groupby))
    bins_with_data = len(groups)

    groups = list(group_records_with_padding(user.records, groupby=groupby))
    bins = len(groups)
    bins_without_data = bins - bins_with_data

    reporting = OrderedDict([
        ('antennas_path', user.antennas_path),
        ('attributes_path', user.attributes_path),
        ('recharges_path', user.attributes_path),
        ('version', bc.__version__),
        ('code_signature', bc.helper.tools.bandicoot_code_signature()),
        ('groupby', groupby),
        ('split_week', split_week),
        ('split_day', split_day),
        ('start_time', user.start_time and str(user.start_time)),
        ('end_time', user.end_time and str(user.end_time)),
        ('night_start', str(user.night_start)),
        ('night_end', str(user.night_end)),
        ('weekend', user.weekend),
        ('number_of_records', len(user.records)),
        ('number_of_antennas', len(user.antennas)),
        ('number_of_recharges', len(user.recharges)),
        ('bins', bins),
        ('bins_with_data', bins_with_data),
        ('bins_without_data', bins_without_data),
        ('has_call', user.has_call),
        ('has_text', user.has_text),
        ('has_home', user.has_home),
        ('has_recharges', user.has_recharges),
        ('has_attributes', user.has_attributes),
        ('has_network', user.has_network),
        ('percent_records_missing_location', bc.helper.tools.percent_records_missing_location(user)),
        ('antennas_missing_locations', bc.helper.tools.antennas_missing_locations(user)),
        ('percent_outofnetwork_calls', user.percent_outofnetwork_calls),
        ('percent_outofnetwork_texts', user.percent_outofnetwork_texts),
        ('percent_outofnetwork_contacts', user.percent_outofnetwork_contacts),
        ('percent_outofnetwork_call_durations', user.percent_outofnetwork_call_durations),
    ])

    if user.ignored_records is not None:
        reporting['ignored_records'] = OrderedDict(user.ignored_records)

    returned = OrderedDict([
        ('name', user.name),
        ('reporting', reporting)
    ])

    for fun, datatype in functions:
        try:
            metric = fun(user, groupby=groupby, summary=summary,
                         datatype=datatype, filter_empty=filter_empty,
                         split_week=split_week, split_day=split_day)
        except ValueError:
            metric = fun(user, groupby=groupby, datatype=datatype,
                         split_week=split_week, filter_empty=filter_empty,
                         split_day=split_day)

        returned[fun.__name__] = metric

    if network and user.has_network:
        for fun in network_functions:
            returned[fun.__name__] = fun(user)

    if attributes and user.attributes != {}:
        returned['attributes'] = OrderedDict(user.attributes)

    if flatten is True:
        return globals()['flatten'](returned)

    return returned
