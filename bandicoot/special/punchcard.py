

import bandicoot as bc
import datetime as dt
import itertools
import csv
from bisect import bisect_right
from bandicoot.helper.group import group_records
from bandicoot.helper.tools import unique, flatten_list
from bandicoot.utils import flatten
from bandicoot.core import User, Record
from functools import partial
from math import floor


def create_punchcards(user, split_interval=60):
    """
    Computes raw indicators (e.g. number of outgoing calls) for intervals of ~1 hour
    across each week of user data. These "punchcards" are returned in a nested list
    with each sublist containing [user.name, channel, weekday, section, value].

    Parameters
    ----------
    user : object
        The user to create punchcards for.
    split_interval : int
        The interval in minutes for which each indicator is computed. Defaults to 60.
        Needs to be able to split a day (24*60 minutes) evenly.
    """

    if not float(24*60/split_interval).is_integer():
        raise ValueError(
            "The minute interval set for the punchcard structure does not evenly divide the day!")

    contacts_in = partial(bc.individual.number_of_contacts,
                          direction='in', summary=None, return_list=True)
    contacts_out = partial(bc.individual.number_of_contacts,
                           direction='out', summary=None, return_list=True)
    calls_in = partial(bc.individual.number_of_interactions,
                       direction='in', interaction='call', summary=None, return_list=True)
    calls_out = partial(bc.individual.number_of_interactions,
                        direction='out', interaction='call', summary=None, return_list=True)
    texts_in = partial(bc.individual.number_of_interactions,
                       direction='in', interaction='text', summary=None, return_list=True)
    texts_out = partial(bc.individual.number_of_interactions,
                        direction='out', interaction='text', summary=None, return_list=True)
    time_spent_in = partial(bc.individual.call_duration,
                          direction='in', interaction='call', summary=None, return_list=True)
    time_spent_out = partial(bc.individual.call_duration,
                           direction='out', interaction='call', summary=None, return_list=True)

    core_func = [
        (contacts_in, _sum_options),
        (contacts_out, _sum_options),
        (calls_in, _sum_options),
        (calls_out, _sum_options),
        (texts_in, _sum_options),
        (texts_out, _sum_options)
    ]

    time_func = [
        (time_spent_in, _sum_options),
        (time_spent_out, _sum_options)
    ]

    pc = []
    sections = [(i+1)*split_interval for i in range(7*24*60/split_interval)]
    temp_user = _extract_user_info(user)
    
    for grouped_records in group_records(user, groupby='week'):
        week_records = list(grouped_records)
        time_spent_rec = _transform_to_time_spent(week_records, split_interval, sections)
        pc.extend(_calculate_channels(
            week_records, sections, split_interval, core_func, temp_user))
        pc.extend(_calculate_channels(
            time_spent_rec, sections, split_interval, time_func, temp_user, len(core_func)))

    return pc


def export_punchcards(punchcards, filename, digits=5):
    """
    Exports a list of punchcards to a specified filename in the CSV format.

    Parameters
    ----------
    punchcards : list
        The punchcards to export.
    filename : string
        Path for the exported CSV file.
    """

    with open(filename, 'wb') as f:
        w = csv.writer(f)
        w.writerow(['year_week', 'channel', 'weekday', 'section', 'value'])

        def make_repr(item):
            if item is None:
                return None
            elif isinstance(item, float):
                return repr(round(item, digits))
            else:
                return str(item)

        for row in punchcards:
            w.writerow([make_repr(item) for item in row])

    print "Successfully exported {} raw punchcard values to {}".format(len(punchcards), filename)


def read_punchcards(filename):
    """
    Read a list of punchcards from a CSV file.
    """

    with open(filename, 'rb') as f:
        r = csv.reader(f)
        pc = list(r)
    
    # remove header and convert to numeric
    pc.pop(0)  
    for i, row in enumerate(pc):
        row[1:4] = map(int, row[1:4])
        row[4] = float(row[4])

    print "Successfully loaded {} raw punchcard values from %s".format(len(pc), filename)    
    return pc


def _calculate_channels(records, sections, split_interval, channel_funcs, user, c_start=0):
    """
    Used to group a list of records across a week as defined by the supplied sections.
    Outputs a list containing records in each section and a list with info to identify those sections.

    Parameters
    ----------
    records : list
        The week of records to calculate the channels for.
    sections : list
        The list of sections for grouping. Each section will have an integer value
        stating the minutes away from midnight between Sunday and Monday.
    split_interval : int
        The interval in minutes for which each indicator is computed.
    channel_funcs : list
        Indicator functions that generate the values for the punchcard.
    user : object
        The user to calculate channels for.
    c_start : num
        Start numbering of channels from this value. Optional parameter. Default value of 0.
        Used when adding channels to the same user using different lists of records.
    """    

    
    """
    Computes the channels as specified by the parameter ``channel_funcs`` for a week of records.
    """

    week_matrix = []
    if len(records) == 0:
        return week_matrix

    if not isinstance(records, list):
        records = [records]    
    year_week = str(records[0].datetime.isocalendar()[0])+'-'+str(records[0].datetime.isocalendar()[1])    
    
    section_lists, section_id = _punchcard_grouping(records, sections, split_interval)
    for c, fun in enumerate(channel_funcs):
        for b, section_records in enumerate(section_lists):
            for inner_f, outer_f in [fun]:
                try:
                    user._records = section_records # _records is used to avoid recomputing home
                    indicator = float(outer_f(inner_f(user)))
                    if indicator != 0:
                        week_matrix.append([year_week, c+c_start, section_id[b][0], section_id[b][1], indicator])
                except (TypeError, ValueError, IndexError) as e:
                    raise ValueError(
                        "Failed to compute channel {} for user {}".format(c+c_start, user.name))

    return week_matrix


def _punchcard_grouping(records, sections, split_interval):
    """
    Used to group a list of records across a week as defined by the supplied sections.
    Outputs a list containing records in each section and a list with info to identify those sections.

    Parameters
    ----------
    records : list
        The week of records to group across the different weekdays/sections.
    sections : list
        The list of sections for grouping. Each section will have an integer value
        stating the minutes away from midnight between Sunday and Monday.
    split_interval : int
        The interval in minutes for which each indicator is computed.
    """

    def _group_by_weektime(records, sections):
        for _, group in itertools.groupby(records, key=lambda r: bisect_right(sections, _find_weektime(r.datetime))):
            yield group

    section_records = _group_by_weektime(records, sections)
    section_lists = _extract_list_from_generator(section_records)
    section_indices = [bisect_right(sections, _find_weektime(r_list[0].datetime)) for r_list in section_lists]
    section_id = _find_day_section_from_indices(section_indices, split_interval)    
    assert(len(section_lists) == len(section_id) and len(section_indices) == len(unique(section_indices)))

    return section_lists, section_id


def _transform_to_time_spent(records, split_interval, sections):
    """
    Each call that crosses a boundary of the sections in the punchcard is split.
    These new records contain the amount of time (in record.call_duration) spent
    talking in that specific section.
    """

    t_records = []

    # contrary to the rest of the binning process, this is done with second precision
    for r in filter(lambda rec: rec.interaction == 'call' and rec.call_duration > 0, records):
        t_left = r.call_duration
        t_to_next_section = _seconds_to_section_split(r, sections)
        t_spent_total = 0

        while (t_left > 0):
            t_spent = min(t_to_next_section, t_left)
            t_left -= t_spent
            t_records.append(Record(
                'call', r.direction, None, r.datetime + dt.timedelta(seconds=t_spent_total), t_spent, None))
            t_spent_total += t_spent
            t_to_next_section = split_interval*60

    return sorted(t_records, key= lambda r: _find_weektime(r.datetime))


def _extract_user_info(user):
    """
    Creates a new user class with extracted user attributes for later use.
    A new user is needed when wanting to avoid overwritting e.g. ``user.records``.
    """

    temp_user = User()
    copy_attributes = [
        'antennas', 'name', 'night_start', 'night_end', 'weekend', 'home']

    for attr in copy_attributes:
        setattr(temp_user, attr,  getattr(user, attr))

    return temp_user


def _find_weektime(datetime, time_type='min'):
    """
    Finds the minutes/seconds aways from midnight between Sunday and Monday.

    Parameters
    ----------
    datetime : datetime
        The date and time that needs to be converted.
    time_type : 'min' or 'sec'
        States whether the time difference should be specified in seconds or minutes.
    """

    if time_type == 'sec':
        return datetime.weekday()*24*60*60 + datetime.hour*60*60 + datetime.minute*60 + datetime.second
    elif time_type == 'min':
        return datetime.weekday()*24*60 + datetime.hour*60 + datetime.minute
    else:
        raise ValueError("Invalid time type specified.")


def _extract_list_from_generator(generator):
    """
    Iterates over a generator to extract all the objects and add them to a list.
    Useful when the objects have to be used multiple times.
    """

    extracted = []
    for i in generator:
        extracted.append(list(i))
    return extracted


def _seconds_to_section_split(record, sections):
    """
    Finds the seconds to the next section from the datetime of a record.
    """    
    
    next_section = sections[bisect_right(sections, _find_weektime(record.datetime))]*60
    return next_section - _find_weektime(record.datetime, time_type='sec')


def _find_day_section_from_indices(indices, split_interval):
    """
    Returns a list with [weekday, section] identifiers found using a list of indices.
    """        
    
    cells_day = 24*60/split_interval
    return [[int(floor(i/cells_day)), i%cells_day] for i in indices]
    

def _sum_options(data, replace_none=True):  
    if replace_none:
        data = [0 if x == None else x for x in data]
    return sum(data)
