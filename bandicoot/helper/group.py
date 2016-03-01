from functools import partial
from datetime import timedelta
from collections import OrderedDict
import itertools

from bandicoot.helper.maths import mean, std, SummaryStats
from bandicoot.helper.tools import advanced_wrap, AutoVivification


DATE_GROUPERS = {
    None: lambda d: None,
    "day": lambda d: d.isocalendar(),
    "week": lambda d: d.isocalendar()[0:2],
    "month": lambda d: (d.year, d.month),
    "year": lambda d: d.year
}


def filter_records(user, interaction=None, part_of_week='allweek', part_of_day='allday'):
    """
    Filter records of a User objects by interaction, part of week and day.

    Parameters
    ----------
    user : User
        a bandicoot User object
    part_of_week : {'allweek', 'weekday', 'weekend'}, default 'allweek'
        * 'weekend': keep only the weekend records
        * 'weekday': keep only the weekdays records
        * 'allweek': use all the records
    part_of_day : {'allday', 'day', 'night'}, default 'allday'
        * 'day': keep only the records during the day
        * 'night': keep only the records during the night
        * 'allday': use all the records
    interaction : object
        The interaction to filter records:
        * "callandtext", for only callandtext;
        * a string, to filter for one type;
        * None, to use all records.
    """

    records = user.records
    if interaction == 'callandtext':
        records = filter(lambda r: r.interaction in ['call', 'text'], records)
    elif interaction is not None:
        records = filter(lambda r: r.interaction == interaction, records)

    if part_of_week == 'weekday':
        records = filter(lambda r: r.datetime.isoweekday() not in user.weekend, records)
    elif part_of_week == 'weekend':
        records = filter(lambda r: r.datetime.isoweekday() in user.weekend, records)
    elif part_of_week != 'allweek':
        raise KeyError("{} is not a valid value for part_of_week. it should be 'weekday', 'weekend' or 'allweek'.".format(part_of_week))

    if user.night_start < user.night_end:
        night_filter = lambda r: user.night_end > r.datetime.time() > user.night_start
    else:
        night_filter = lambda r: not(user.night_end < r.datetime.time() < user.night_start)

    if part_of_day == 'day':
        records = filter(lambda r: not(night_filter(r)), records)
    elif part_of_day == 'night':
        records = filter(night_filter, records)
    elif part_of_day != 'allday':
        raise KeyError("{} is not a valid value for part_of_day. It should be 'day', 'night' or 'allday'.".format(part_of_day))

    return records


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


def _group_range(records, method):
    """
    Yield the range of all dates between the extrema of
    a list of records, separated by a given time delta.
    """

    start_date = records[0].datetime
    end_date = records[-1].datetime
    _fun = DATE_GROUPERS[method]

    d = start_date

    # Day and week use timedelta
    if method not in ["month", "year"]:
        def increment(i):
            return i + timedelta(**{method + 's': 1})

    elif method == "month":
        def increment(i):
            year, month = divmod(i.month + 1, 12)
            if month == 0:
                month = 12
                year = year - 1
            return d.replace(year=d.year + year, month=month)

    elif method == "year":
        def increment(i):
            return d.replace(year=d.year + 1)

    while _fun(d) <= _fun(end_date):
        yield d
        d = increment(d)


def group_records_with_padding(records, groupby='week', time_binning=False):
    if groupby is None:
        if time_binning:
            yield _binning(records)
        else:
            yield records
        return

    if records == []:
        return

    _range = _group_range(records, groupby)
    _fun = DATE_GROUPERS[groupby]

    # Ad hoc grouping with padding
    pointer = next(_range)
    for key, chunk in itertools.groupby(records, key=lambda r: _fun(r.datetime)):
        chunk = list(chunk)

        while _fun(pointer) < key:
            yield []
            pointer = next(_range)

        if time_binning:
            yield _binning(chunk)
        else:
            yield chunk

        pointer = next(_range)


def group_records(records, groupby='week', time_binning=False):
    """
    Group records by year, month, week, or day.

    Parameters
    ----------
    records : iterator
        An iterator over records

    groupby : Default is 'week':
        * 'week': group all records by year and week
        * None: records are not grouped. This is useful if you don't want to
          divide records in chunks
        * "day", "month", and "year" also accepted
    """

    def _group_date(records, _fun):
        for _, chunk in itertools.groupby(records, key=lambda r: _fun(r.datetime)):
            yield list(chunk)

    groups = _group_date(records, DATE_GROUPERS[groupby])

    if time_binning:
        return map(_binning, groups)
    else:
        return groups


def infer_type(data):
    """
    Infer the type of objects returned by indicators.

    infer_type returns:
     - 'scalar' for a number or None,
     - 'summarystats' for a SummaryStats object,
     - 'distribution_scalar' for a list of scalars,
     - 'distribution_summarystats' for a list of SummaryStats objects
    """

    if isinstance(data, (type(None), int, float)):
        return 'scalar'

    if isinstance(data, SummaryStats):
        return 'summarystats'

    if hasattr(data, "__len__"):  # list or numpy array
        data = filter(lambda x: x is not None, data)
        if len(data) == 0 or isinstance(data[0], (int, float)):
            return 'distribution_scalar'
        if isinstance(data[0], SummaryStats):
            return 'distribution_summarystats'

        raise TypeError("{} is not a valid input. It should be a number, a SummaryStats object, or None".format(data[0]))

    raise TypeError("{} is not a valid input. It should be a number, a SummaryStats object, or a list".format(data))


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

    if datatype is None:
        datatype = infer_type(data)

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
        if summary == 'default':
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

    raise ValueError("{} is not a valid data type.".format(datatype))


def _generic_wrapper(f, user_kwd, summary, time_binning, user, groupby, filter_empty, datatype, parameters, **kwargs):
    def compute_indicator(g):
        if user_kwd:
            return f(g, user, **kwargs)
        else:
            return f(g, **kwargs)

    def _ordereddict_product(dicts):
        return [OrderedDict(zip(dicts, x)) for x in itertools.product(*dicts.values())]

    def filter_and_map():
        """
        Call the wrapped function for every combinations of
        part_of_week and part_of_day.
        """

        for params in _ordereddict_product(parameters):
            records = filter_records(user, **params)
            if filter_empty:
                result = [compute_indicator(g) for g in group_records(records, groupby, time_binning)]
            else:
                result = [compute_indicator(g) for g in group_records_with_padding(records, groupby, time_binning)]
            yield tuple(params.values()) + (result, )

    returned = AutoVivification()  # nested dict structure
    for params_result in filter_and_map():
        params = params_result[:-1]
        m = params_result[-1]

        if groupby is None:
            m = m[0] if len(m) != 0 else None

        stats = statistics(m, summary=summary, datatype=datatype)
        returned.insert(params, stats)

    return returned


def grouping(f=None, user_kwd=False, interaction=['call', 'text'], summary='default'):
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

    def wrapper(user, groupby='week', interaction=interaction, summary=summary, split_week=False, split_day=False, filter_empty=True, datatype=None, **kwargs):
        if interaction is None:
            interaction = ['call', 'text']
        elif isinstance(interaction, str):
            interaction = [interaction]
        else:
            interaction = interaction[:]  # copy the list for more safety

        parameters = OrderedDict([
            ('part_of_week', ['allweek']),
            ('part_of_day', ['allday']),
            ('interaction', interaction)
        ])

        if split_day:
            parameters['part_of_day'] += ['day', 'night']

        if split_week:
            parameters['part_of_week'] += ['weekday', 'weekend']

        for i in interaction:
            if i not in ['callandtext', 'call', 'text', 'location']:
                raise ValueError("%s is not a valid interaction value. Only 'call', "
                                 "'text', and 'location' are accepted." % i)

        return _generic_wrapper(f, user_kwd, summary, False, user, groupby, filter_empty, datatype, parameters, **kwargs)

    return advanced_wrap(f, wrapper)


def spatial_grouping(f=None, user_kwd=False, summary='default', time_binning=True):
    if f is None:
        return partial(spatial_grouping, user_kwd=user_kwd, summary=summary,
                       time_binning=time_binning)

    def wrapper(user, groupby='week', summary=summary, split_week=False, split_day=False, filter_empty=True, datatype=None, **kwargs):
        parameters = OrderedDict([
            ('part_of_week', ['allweek']),
            ('part_of_day', ['allday'])
        ])

        if split_day:
            parameters['part_of_day'] += ['day', 'night']

        if split_week:
            parameters['part_of_week'] += ['weekday', 'weekend']

        return _generic_wrapper(f, user_kwd, summary, time_binning, user, groupby, filter_empty, datatype, parameters)

    return advanced_wrap(f, wrapper)
