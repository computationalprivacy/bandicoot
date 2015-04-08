from bandicoot.helper.tools import OrderedDict
from bandicoot.helper.group import group_records
import bandicoot as bc

from functools import partial

try:
    next
except NameError:
    from bandicoot.helper.fixes import next


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


def all(user, groupby='week', summary='default', attributes=True, flatten=False):
    """
    Return a dictionary containing all bandicoot metrics for a given user,
    as well as reporting variables such as the percentage of records
    missing a location.
    """

    scalar_type = 'distribution_scalar' if groupby == 'week' else 'scalar'
    summary_type = 'distribution_summarystats' if groupby == 'week' else 'summarystats'

    number_of_interactions_in = partial(bc.individual.number_of_interactions, direction='in')
    number_of_interactions_in.__name__ = 'number_of_interaction_in'
    number_of_interactions_out = partial(bc.individual.number_of_interactions, direction='out')
    number_of_interactions_out.__name__ = 'number_of_interaction_out'

    functions = [
        (bc.individual.active_days, scalar_type),
        (bc.individual.number_of_contacts, scalar_type),
        (bc.individual.call_duration, summary_type),
        (bc.individual.percent_nocturnal, scalar_type),
        (bc.individual.percent_initiated_conversation, scalar_type),
        (bc.individual.percent_initiated_interactions, scalar_type),
        (bc.individual.response_delay_text, summary_type),
        (bc.individual.response_rate_text, scalar_type),
        (bc.individual.entropy_of_contacts, scalar_type),
        (bc.individual.balance_contacts, summary_type),
        (bc.individual.interactions_per_contact, summary_type),
        (bc.individual.interevents_time, summary_type),
        (bc.individual.number_of_contacts_xpercent_interactions, scalar_type),
        (bc.individual.number_of_contacts_xpercent_durations, scalar_type),
        (bc.individual.number_of_interactions, scalar_type),
        (number_of_interactions_in, scalar_type),
        (number_of_interactions_out, scalar_type),
        (bc.spatial.number_of_places, scalar_type),
        (bc.spatial.entropy_places, scalar_type),
        (bc.spatial.percent_at_home, scalar_type),
        (bc.spatial.radius_of_gyration, scalar_type),
        (bc.spatial.frequent_locations, scalar_type)
    ]

    groups = [[r for r in g] for g in group_records(user, groupby=groupby)]

    reporting = OrderedDict([
        ('antennas_path', user.antennas_path),
        ('attributes_path', user.attributes_path),
        ('version', bc.__version__),
        ('groupby', groupby),
        ('start_time', user.start_time and str(user.start_time)),
        ('end_time', user.end_time and str(user.end_time)),
        ('bins', len(groups)),
        ('has_call', user.has_call),
        ('has_text', user.has_text),
        ('has_home', user.has_home),
        ('percent_records_missing_location', bc.helper.tools.percent_records_missing_location(user)),
        ('antennas_missing_locations', bc.helper.tools.antennas_missing_locations(user)),
        ('percent_outofnetwork_calls', user.percent_outofnetwork_calls),
        ('percent_outofnetwork_texts', user.percent_outofnetwork_texts),
        ('percent_outofnetwork_contacts', user.percent_outofnetwork_contacts),
        ('percent_outofnetwork_call_durations', user.percent_outofnetwork_call_durations),
    ])

    if user.records is not None:
        reporting['number_of_records'] = sum(map(len, groups))
    else:
        reporting['number_of_records'] = 0.

    if user.ignored_records is not None:
        reporting['ignored_records'] = user.ignored_records

    returned = OrderedDict([
        ('name', user.name),
        ('reporting', reporting)
    ])

    for fun, datatype in functions:
        try:
            metric = fun(user, groupby=groupby, summary=summary, datatype=datatype)
        except ValueError:
            metric = fun(user, groupby=groupby, datatype=datatype)
        returned[fun.__name__] = metric

    if attributes and user.attributes != {}:
        returned['attributes'] = user.attributes

    if flatten is True:
        return globals()['flatten'](returned)

    return returned
