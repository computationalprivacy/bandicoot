from functools import partial
import itertools
from bandicoot.helper.tools import mean, std, SummaryStats, advanced_wrap


def group_records(user, interaction=None, groupby='week', day_type=None, time_type=None):
    """
    Group records by year and week number. This function is used by the
    ``@grouping`` decorator.

    Parameters
    ----------
    records : iterator
        An iterator over records

    groupby : {'week', None}, default 'week'
        * 'week': group all records by year and week;
        * None: records are not grouped. This is useful if you don't want to
          divide records in chunks.
    interaction : object
        The interaction to filter records:
        * "callandtext", for only callandtext;
        * a string, to filter for one type;
        * None, to use all records.
    """

    records = user.records

    def _group_date(records, _fun):
        for _, chunk in itertools.groupby(records, key=lambda r: _fun(r.datetime)):
            yield chunk

    if interaction == 'callandtext':
        records = filter(lambda r: r.interaction in ['call', 'text'], records)
    elif interaction is not None:
        records = filter(lambda r: r.interaction == interaction, records)

    if day_type == 'weekday':
        records = filter(lambda r: r.datetime.isoweekday() not in [6, 7], records)
    elif day_type == 'weekend':
        records = filter(lambda r: r.datetime.isoweekday() in [6, 7], records)
    elif day_type is not None:
        raise KeyError("%s is not a valid value for day_type. it should be 'weekday', 'weekend' or None.")

    if user.night_start < user.night_end:
        night_filter = lambda r: user.night_end > r.datetime.time() > user.night_start
    else:
        night_filter = lambda r: not(user.night_end < r.datetime.time() < user.night_start)

    if time_type == 'day':
        records = filter(night_filter, records)
    elif time_type == 'night':
        records = filter(lambda r: not(night_filter(r)), records)
    elif time_type is not None:
        raise KeyError("%s is not a valid value for time_type. it should be 'day', 'night' or None.")

    if groupby is None:
        return _group_date(records, lambda _: None)
    else:
        return _group_date(records, lambda d: d.isocalendar()[:2])


def statistics(data, summary='default', datatype=None):
    """
    Return statistics (mean, standard error, standard error and median, min and max) on data metrics.

    Examples
    --------
    Given a list of integers or floating point numbers,
    ``statistics`` computes the mean and standard error of the mean, and the min and max.

    >>> statistics([0, 1, 2, 3])
    {'mean': 1.5, 'std': 1.2910, 'min': 0, 'max': 3}

    Given a list of ``SummaryStats`` tuples, the function will
    returns the mean, standard error of the mean, min and max for each attribute
    of the tuples.
    """

    def _default_stats(agg):
        if agg is None or len(agg) == 0:
            return {'mean': None, 'std': None}
        else:
            # Some functions may return None values
            # It's better to filter them
            agg = filter(lambda x: x is not None, agg)
            return {'mean': mean(agg), 'std': std(agg)}

    def _stats_dict(v):
        return {key: _default_stats([getattr(s, key, None) for s in data]) for key in v}

    summary_keys = {
        'default': ['mean', 'std'],
        'extended': ['mean', 'std', 'median', 'skewness', 'kurtosis', 'min', 'max']
    }

    # Infer the data type of 'data'
    if datatype is None:
        if isinstance(data, (type(None), int, float)):
            datatype = 'scalar'
        elif isinstance(data, SummaryStats):
            datatype = 'summarystats'
        elif hasattr(data, "__len__"):  # list or numpy array
            data = filter(lambda x: x is not None, data)
            if len(data) == 0 or isinstance(data[0], (int, float)):
                datatype = 'distribution_scalar'
            elif isinstance(data[0], SummaryStats):
                datatype = 'distribution_summarystats'
            else:
                raise TypeError("{} is not a valid input. It should be a number, a SummaryStats object, or None".format(data[0]))
        else:
            raise TypeError("{} is not a valid input. It should be a number, a SummaryStats object, or a list".format(data))

    if datatype == 'scalar':
        return data

    if datatype == 'summarystats':
        if summary is None:
            return data.distribution
        elif summary in ['default', 'extended']:
            return {key: getattr(data, key, None) for key in summary_keys[summary]}
        else:
            raise ValueError("{} is not a valid summary type".format(summary))

    if datatype == 'distribution_scalar':
        if summary is 'default':
            return _default_stats(data)
        elif summary is None:
            return data
        else:
            raise ValueError("{} is not a valid summary type".format(summary))

    if datatype == 'distribution_summarystats':
        if summary is None:
            return [item.distribution for item in data]
        elif summary in ['extended', 'default']:
            return _stats_dict(summary_keys[summary])
        else:
            raise ValueError("{} is not a valid summary type".format(summary))

    else:
        raise ValueError("{} is not a valid data type.".format(datatype))


def grouping(f=None, user_kwd=False, interaction=None, summary='default'):
    """
    ``grouping`` is a decorator for indicator functions, used to simplify the source code.

    Parameters
    ----------
    f : function
        The function to decorate
    user_kwd : boolean
        If user_kwd is True, the user object will be passed to the decorated function
    interaction : 'call', 'text', 'location', or a list
        By default, all indicators use only 'call' and 'text' records, but the
        interaction keywords filters the records passed to the function.
    summary: 'default', 'extended', None
        An indicator returns data statistics, ether *mean* and *std* by
        default, more with 'extended', or the inner distribution with None.
        See :meth:`~bandicoot.helper.group.statistics` for more details.


    See :ref:`new-indicator-label` to learn how to write an indicator with this decorator.

    """

    if f is None:
        return partial(grouping, user_kwd=user_kwd, interaction=interaction, summary=summary)

    def wrapper(user, groupby='week', interaction=interaction, summary=summary, day_type=None, time_type=None, datatype=None, **kwargs):
        if interaction is None:
            interaction = ['call', 'text']
        elif isinstance(interaction, str):
            interaction = [interaction]

        for i in interaction:
            if i not in ['callandtext', 'call', 'text', 'location']:
                raise ValueError("%s is not a valid interaction value. Only 'call', "
                                 "'text', and 'location' are accepted." % i)

        mapped = ((i, [f(g, user, **kwargs)
                  if user_kwd is True else f(g, **kwargs) for g in
                  group_records(user, groupby=groupby, interaction=i, day_type=day_type, time_type=time_type)])
                  for i in interaction)

        returned = {}

        for (k, m) in mapped:
            if groupby is None:
                m = m[0] if len(m) != 0 else None
            returned[k] = statistics(m, summary=summary, datatype=datatype)

        return returned

    return advanced_wrap(f, wrapper)


def _binning(records):
    """
    Bin records by chunks of 30 minutes, returning the most prevalent position.
    """

    records = list(records)

    from collections import Counter

    def get_key(d):
        from datetime import datetime, timedelta
        k = d + timedelta(minutes=-(d.minute % 30))
        return datetime(k.year, k.month, k.day, k.hour, k.minute, 0)

    chunks = itertools.groupby(records, key=lambda r: get_key(r.datetime))

    for _, items in chunks:
        positions = [i.position for i in items]
        yield Counter(positions).most_common(1)[0][0]


def spatial_grouping(f=None, user=False, summary='default', use_records=False):
    if f is None:
        return partial(spatial_grouping, user=user, summary=summary,
                       use_records=use_records)

    if use_records is True:
        map_records = lambda x: x
    else:
        map_records = _binning

    def wrapper(_user, groupby='week', summary=summary, day_type=None, time_type=None, datatype=None, **kwargs):
        m = [f(map_records(g), _user, **kwargs) if user is True else f(map_records(g), **kwargs) for g in
             group_records(_user, groupby=groupby, interaction=None, day_type=day_type, time_type=time_type)]

        if groupby is None:
            m = m[0] if len(m) != 0 else None

        return statistics(m, summary=summary, datatype=datatype)

    return advanced_wrap(f, wrapper)
