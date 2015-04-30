from functools import partial
import itertools
from bandicoot.helper.tools import mean, std, SummaryStats, advanced_wrap, warning_str, AutoVivification


def group_records(user, interaction=None, groupby='week', part_of_week='allweek', part_of_day='allday'):
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

    def _group_date(records, _fun):
        for _, chunk in itertools.groupby(records, key=lambda r: _fun(r.datetime)):
            yield chunk

    if interaction == 'callandtext':
        records = filter(lambda r: r.interaction in ['call', 'text'], records)
    elif interaction is not None:
        records = filter(lambda r: r.interaction == interaction, records)

    if part_of_week == 'weekday':
        records = filter(lambda r: r.datetime.isoweekday() not in user.weekend, records)
    elif part_of_week == 'weekend':
        records = filter(lambda r: r.datetime.isoweekday() in user.weekend, records)
    elif part_of_week is not 'allweek':
        raise KeyError("{} is not a valid value for part_of_week. it should be 'weekday', 'weekend' or 'allweek'.".format(part_of_week))

    if user.night_start < user.night_end:
        night_filter = lambda r: user.night_end > r.datetime.time() > user.night_start
    else:
        night_filter = lambda r: not(user.night_end < r.datetime.time() < user.night_start)

    if part_of_day == 'day':
        records = filter(night_filter, records)
    elif part_of_day == 'night':
        records = filter(lambda r: not(night_filter(r)), records)
    elif part_of_day is not 'allday':
        raise KeyError("{} is not a valid value for part_of_day. It should be 'day', 'night' or 'allday'.".format(part_of_day))

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

    def wrapper(user, groupby='week', interaction=interaction, summary=summary, split_week=False, split_day=False, datatype=None, **kwargs):
        if interaction is None:
            interaction = ['call', 'text']
        elif isinstance(interaction, str):
            interaction = [interaction]
        else:
            interaction = interaction[:]  # copy the list for more safety

        part_of_day = ['allday']
        if split_day:
            part_of_day += ['day', 'night']

        part_of_week = ['allweek']
        if split_week:
            part_of_week += ['weekday', 'weekend']

        for i in interaction:
            if i not in ['callandtext', 'call', 'text', 'location']:
                raise ValueError("%s is not a valid interaction value. Only 'call', "
                                 "'text', and 'location' are accepted." % i)

        def map_filters(interaction, part_of_week, part_of_day):
            """
            Call the wrapped function for every combinations of interaction,
            part_of_week, and part_of_day.
            """
            for i in interaction:
                for filter_week in part_of_week:
                    for filter_day in part_of_day:
                        if user_kwd is True:
                            result = [f(g, user, **kwargs) for g in group_records(user, i, groupby, filter_week, filter_day)]
                        else:
                            result = [f(g, **kwargs) for g in group_records(user, i, groupby, filter_week, filter_day)]

                        yield filter_week, filter_day, i, result

        returned = AutoVivification()  # nested dict structure
        for (f_w, f_d, i, m) in map_filters(interaction, part_of_week, part_of_day):
            if groupby is None:
                m = m[0] if len(m) != 0 else None
            returned[f_w][f_d][i] = statistics(m, summary=summary, datatype=datatype)

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


def spatial_grouping(f=None, user_kwd=False, summary='default', use_records=False):
    if f is None:
        return partial(spatial_grouping, user_kwd=user_kwd, summary=summary,
                       use_records=use_records)

    if use_records is True:
        map_records = lambda x: x
    else:
        map_records = _binning

    def wrapper(user, groupby='week', summary=summary, split_week=False, split_day=False, datatype=None, **kwargs):
        part_of_day = ['allday']
        if split_day:
            part_of_day += ['day', 'night']

        part_of_week = ['allweek']
        if split_week:
            part_of_week += ['weekday', 'weekend']

        def map_filters_spatial(part_of_week, part_of_day):
            """
            Call the wrapped function for every combinations of interaction,
            part_of_week, and part_of_day.
            """
            for filter_week in part_of_week:
                for filter_day in part_of_day:
                    if user_kwd is True:
                        result = [f(map_records(g), user, **kwargs) for g in group_records(user, None, groupby, filter_week, filter_day)]
                    else:
                        result = [f(map_records(g), **kwargs) for g in group_records(user, None, groupby, filter_week, filter_day)]

                    yield filter_week, filter_day, result

        returned = AutoVivification()  # nested dict structure
        for (f_w, f_d, m) in map_filters_spatial(part_of_week, part_of_day):
            if groupby is None:
                m = m[0] if len(m) != 0 else None
            returned[f_w][f_d] = statistics(m, summary=summary, datatype=datatype)

        return returned

    return advanced_wrap(f, wrapper)
