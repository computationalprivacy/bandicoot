"""
Contains tools for processing files (reading and writing csv and json files).
"""

from __future__ import with_statement, division

from bandicoot.helper.tools import OrderedDict

from bandicoot.core import User, Record, Position
from bandicoot.helper.tools import percent_records_missing_location, antennas_missing_locations, warning_str
from bandicoot.utils import flatten

from datetime import datetime
from json import dumps
from collections import Counter
import csv
import sys
import os


def to_csv(objects, filename, digits=5):
    """
    Export the flatten indicators of one or several users to CSV.

    Parameters
    ----------
    objects : list
        List of objects to be exported.
    filename : string
        File to export to.
    digits : int
        Precision of floats.

    Examples
    --------
    This function can be use to export the results of :meth`bandicoot.utils.all`.
    >>> U_1 = bc.User()
    >>> U_2 = bc.User()
    >>> bc.to_csv([bc.utils.all(U_1), bc.utils.all(U_2)], 'results_1_2.csv')

    If you only have one object, you can simply pass it as argument:
    >>> bc.to_csv(bc.utils.all(U_1), 'results_1.csv')
    """

    if not isinstance(objects, list):
        objects = [objects]

    data = [flatten(obj) for obj in objects]
    all_keys = [d for datum in data for d in datum.keys()]
    field_names = sorted(set(all_keys), key=lambda x: all_keys.index(x))

    with open(filename, 'wb') as f:
        w = csv.writer(f)
        w.writerow(field_names)

        def make_repr(item):
            if item is None:
                return None
            elif isinstance(item, float):
                return repr(round(item, digits))
            else:
                return str(item)

        for row in data:
            row = dict((k, make_repr(v)) for k, v in row.items())
            w.writerow([make_repr(row.get(k, None)) for k in field_names])

    print "Successfully exported %d object(s) to %s" % (len(objects), filename)


def to_json(objects, filename):
    """
    Export the indicators of one or several users to JSON.

    Parameters
    ----------
    objects : list
        List of objects to be exported.
    filename : string
        File to export to.

    Examples
    --------
    This function can be use to export the results of :meth`bandicoot.utils.all`.
    >>> U_1 = bc.User()
    >>> U_2 = bc.User()
    >>> bc.to_json([bc.utils.all(U_1), bc.utils.all(U_2)], 'results_1_2.json')

    If you only have one object, you can simply pass it as argument:
    >>> bc.to_json(bc.utils.all(U_1), 'results_1.json')
    """

    if not isinstance(objects, list):
        objects = [objects]

    obj_dict = {obj['name']: obj for obj in objects}

    with open(filename, 'wb') as f:
        f.write(dumps(obj_dict, sort_keys=True, indent=4, separators=(',', ': ')))
    print "Successfully exported %d object(s) to %s" % (len(objects), filename)

def _parse_date(string):
    try:
        return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    except ValueError as ex:
        return ex


def _parse_record(data):

    _map_duration = lambda s: int(s) if s != '' else None

    def _map_position(data):
        antenna = Position()
        if 'antenna_id' in data:
            antenna.antenna = data['antenna_id']
            return antenna
        if 'latitude' in data and 'longitude' in data:
            antenna.position = float(data['latitude']), float(data['longitude'])
        return antenna

    return Record(interaction=data['interaction'],
                  direction=data['direction'],
                  correspondent_id=data['correspondent_id'],
                  datetime=_parse_date(data['datetime']),
                  call_duration=_map_duration(data['call_duration']),
                  position=_map_position(data))


def filter_record(records):
    """
    Filter records and remove items with missing or inconsistents fields

    Parameters
    ----------

    records : list
        A list of Record objects

    Returns
    -------

    records, ignored : (Record list, dict)
        A tuple of filtered records, and a dictionnary counting the missings fields

    """

    scheme = {
        'interaction': lambda r: r.interaction in ['call', 'text'],
        'direction': lambda r: r.direction in ['in', 'out'],
        'correspondent_id': lambda r: r.correspondent_id is not None,
        'datetime': lambda r: isinstance(r.datetime, datetime),
        'call_duration': lambda r: isinstance(r.call_duration, (int, float)) if r.interaction == 'call' else True,
    }

    ignored = OrderedDict([
        ('all', 0),
        ('interaction', 0),
        ('direction', 0),
        ('correspondent_id', 0),
        ('datetime', 0),
        ('call_duration', 0),
    ])

    def _filter(records):
        global removed

        for r in records:
            valid = True
            for key, test in scheme.iteritems():
                if not test(r):
                    ignored[key] += 1
                    valid = False  # Not breaking, we count all fields with errors

            if valid is True:
                yield r
            else:
                ignored['all'] += 1

    return list(_filter(records)), ignored


def load(name, records, antennas, attributes=None, antennas_path=None,
         attributes_path=None, describe=True, warnings=False):
    """
    Creates a new user. This function is used by read_csv, read_orange,
    and read_telenor. If you want to implement your own reader function, we advise you to use the load() function

    `load` will output warnings on the standard output if some records or
    antennas are missing a position.

    Parameters
    ----------

    name : str
        The name of the user. It is stored in User.name and is useful when
        exporting metrics about multiple users.

    records: list
        A list or a generator of Record objects.

    antennas : dict
        A dictionary of the position for each antenna.

    attributes : dict
        A (key,value) dictionary of attributes for the current user

    describe : boolean
        If describe is True, it will print a description of the loaded user
        to the standard output.

    warnings : boolean, default True
        If warnings is equal to False, the function will not output the
        warnings on the standard output.


    For instance:

    .. code-block:: python

       >>> records = [Record(...),...]
       >>> antennas = {'A51': (37.245265, 115.803418),...}
       >>> attributes = {'age': 60}
       >>> load("Frodo", records, antennas, attributes)

    will returns a new User object.


    """

    user = User()
    user.name = name
    user.antennas_path = antennas_path
    user.attributes_path = attributes_path

    user.records, ignored = filter_record(records)

    if ignored['all'] != 0:
        if warnings:
            print warning_str("Warning: %d record(s) were removed due to missing or incomplete fields." % ignored['all'])
        for k in ignored.keys():
            if k != 'all' and warnings:
                print warning_str(" " * 9 + "%s: %i record(s) with incomplete values" % (k, ignored[k]))

    user.ignored_records = dict(ignored)

    if antennas is not None:
        user.antennas = antennas
        user.has_antennas = True
    if attributes is not None:
        user.attributes = attributes

    percent_missing = percent_records_missing_location(user)
    if percent_missing > 0:
        if warnings:
            print warning_str("Warning: {0:.2%} of the records are missing a location.".format(percent_missing))
        if antennas is None and warnings:
            print warning_str("         No antennas file was given and records are using antennas for position")

    if antennas_missing_locations(user) > 0:
        if warnings:
            print warning_str("Warning: %d antenna(s) are missing a location." % antennas_missing_locations(user))

    if describe is True:
        user.describe()

    return user


def _record_match(ours, theirs, time_diff=30):
    """
    Return True if two records match.
    """
    return ours.interaction == theirs.interaction and \
        ours.direction != theirs.direction and \
        ours.call_duration == theirs.call_duration and \
        abs((ours.datetime - theirs.datetime).total_seconds()) < time_diff


def _read_network(user, records_path, attributes_path, read_function, antennas_path=None, extension=".csv"):
    connections = {}
    correspondents = Counter([record.correspondent_id for record in user.records])

    num_records_error = 0

    # Try to load all the possible correspondent files
    for c_id, count in sorted(correspondents.items()):
        correspondent_file = os.path.join(records_path, c_id + extension)
        if os.path.exists(correspondent_file):
            correspondent_user = read_function(c_id, records_path, antennas_path, attributes_path, describe=False, network=False)

            # Look for matching record in the correspondent
            for our_record in filter(lambda x: x.correspondent_id == c_id, user.records):
                for their_record in correspondent_user.records:
                    # See if they match
                    if _record_match(our_record, their_record):
                        break
                else:
                    num_records_error += 1

        else:
            correspondent_user = None

        connections[c_id] = correspondent_user

    if len(user.records) > 0 and num_records_error > 0:
        percent_inconsistant = num_records_error / len(user.records)
        print warning_str('Warning: {} records of the current user are not reciprocated ({:.2%}).'.format(num_records_error, percent_inconsistant))

    # Return the network dictionary sorted by key
    return OrderedDict(sorted(connections.items(), key=lambda t: t[0]))


def read_csv(user_id, records_path, antennas_path=None, attributes_path=None, network=True, describe=True, warnings=True):
    """
    Load user records from a CSV file.

    Parameters
    ----------

    user_id : str
        ID of the user (filename)

    records_path : str
        Path of the directory all the user files.

    antennas_path : str, optional
        Path of the CSV file containing (place_id, latitude, longitude) values.
        This allows antennas to be mapped to their locations.

    attributes_path : str, optional
        Path of the directory containing attributes files (``key, value`` CSV file).
        Attributes can for instance be variables such as like, age, or gender.
        Attributes can be helpful to compute specific metrics.

    network : bool, optional
        If network is True, bandicoot loads the network of the user's correspondants from the same path. Defaults to False.

    describe : boolean
        If describe is True, it will print a description of the loaded user to the standard output.


    Examples
    --------

    >>> user = bandicoot.read_csv('sample_records', '.')
    >>> print len(user.records)
    10

    >>> user = bandicoot.read_csv('sample_records', 'samples', sample_places.csv')
    >>> print len(user.antennas)
    5

    >>> user = bandicoot.read_csv('sample_records', '.', None, 'sample_attributes.csv')
    >>> print user.attributes['age']
    25

    Notes
    -----
    - The csv files can be single, or double quoted if needed.
    - Empty cells are filled with ``None``. For example, if the column
      ``call_duration`` is empty for one record, its value will be ``None``.
      Other values such as ``"N/A"``, ``"None"``, ``"null"`` will be
      considered as a text.
    """

    antennas = None
    if antennas_path is not None:
        with open(antennas_path, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)
            antennas = dict((d['place_id'], (float(d['latitude']),
                                             float(d['longitude'])))
                            for d in reader)

    user_records = os.path.join(records_path, user_id + '.csv')
    with open(user_records, 'rb') as csv_file:
        reader = csv.DictReader(csv_file)
        records = map(_parse_record, reader)

    attributes = None
    if attributes_path is not None:
        user_attributes = os.path.join(attributes_path, user_id + '.csv')
        try:
            with open(user_attributes, 'rb') as csv_file:
                reader = csv.DictReader(csv_file)
                attributes = dict((d['key'], d['value']) for d in reader)
        except IOError:
            attributes = None

    user = load(user_id, records, antennas, attributes, antennas_path,
                attributes_path, describe, warnings)

    # Loads the network
    if network is True:
        user.network = _read_network(user, records_path, attributes_path, read_csv, antennas_path)
        user.recompute_missing_neighbors()

    return user


def read_orange(records_path=None, network=False, describe=True, warnings=True):
    """
    Load user records from a CSV file in *orange* format:

    ``call_record_type;basic_service;user_msisdn;call_partner_identity;datetime;call_duration;longitude;latitude``

    ``basic_service`` takes one of the following values:

    - 11: telephony;
    - 12: emergency calls;
    - 21: short message (in)
    - 22: short message (out)

    Parameters
    ----------

    records_path : str or iterator, optional
        If ``records_path`` is a string, the function will load the CSV file at
        the path ``records_path``. If the parameter is an iterator, records will
        be loaded directly, as an ordered list in the *orange* format.If no
        parameter is included, ``read_orange`` will load records from the
        standard input ``sys.stdin``

    describe : boolean
        If describe is True, it will print a description of the loaded user to the standard output.

    network : bool, optional
        If network is True, bandicoot loads the network of the user's correspondants from the same path. Defaults to False.
    """

    def _parse(reader):
        records = []
        antennas = dict()

        for row in reader:
            direction = 'out' if row[0] == '1' else 'in'
            interaction = 'call' if row[1] in ['11', '12'] else 'text'
            contact = row[3]
            date = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
            call_duration = float(row[5])
            lon, lat = float(row[6]), float(row[7])
            latlon = (lat, lon)

            antenna = None
            for key, value in antennas.items():
                if latlon == value:
                    antenna = key
                    break
            if antenna is None:
                antenna = len(antennas) + 1
                antennas[antenna] = latlon

            position = Position(antenna=antenna, location=latlon)

            record = Record(direction=direction,
                            interaction=interaction,
                            correspondent_id=contact,
                            call_duration=call_duration,
                            datetime=date,
                            position=position)
            records.append(record)

        return records, antennas

    name = records_path

    if isinstance(records_path, str):
        with open(records_path, 'rb') as f:
            reader = csv.reader(f, delimiter=";")
            records, antennas = _parse(reader)

    elif records_path is None:
        reader = csv.reader(sys.stdin, delimiter=";")
        records, antennas = _parse(reader)

    else:
        # Iteration over the first parameter
        records, antennas = _parse(records_path)

    user = load(name, records, antennas, warnings=None, describe=describe)

    if network is True:
        directory = os.path.dirname(records_path)
        user.network = _read_network(user, directory, read_orange)
        user.recompute_missing_neighbors()

    return user


def read_telenor(incoming_cdr, outgoing_cdr, cell_towers, describe=True, warnings=True):
    """
    Load user records from a CSV file in *telenor* format:

    Arguments
    ---------

    incoming_cdr: str
        Path to the CSV file containing incoming records, using the following
        scheme: ::

             B_PARTY,A_PARTY,DURATION,B_CELL,CALL_DATE,CALL_TIME,CALL_TYPE

    outgoing_cdr: str
        Path to the CSV file containing outgoing records, using the following
        scheme: ::

             A_NUMBER,B_NUMBER,DURATION,B_CELL,CALL_DATE,CALL_TIME,CALL_TYPE

    cell_towers: str
        Path to the CSV file containing the positions of all

    describe : boolean
        If describe is True, it will print a description of the loaded user to the standard output.

    """

    import itertools
    import csv

    def parse_direction(code):
        if code == 'MOC':
            return 'out'
        elif code == 'MTC':
            return 'in'
        else:
            raise NotImplementedError

    cells = None
    with open(cell_towers, 'rb') as f:
        cell_towers_list = csv.DictReader(f)
        cells = {}
        for line in cell_towers_list:
            if line['LONGITUDE'] != '' and line['LATITUDE'] != '':
                latlon = (float(line['LONGITUDE']), float(line['LATITUDE']))
                cell_id = line['CELLID_HEX']
                cells[cell_id] = latlon

    def parse_record(raw):
        direction = parse_direction(raw['CALL_TYPE'].strip())

        if direction == 'in':
            contact = raw.get('A_PARTY', raw.get('A_NUMBER'))
            cell_id = raw['B_CELL']
        else:
            contact = raw.get('B_PARTY', raw.get('B_NUMBER'))
            cell_id = raw['A_CELL']

        position = Position(antenna=cell_id, location=cells.get(cell_id))

        _date_str = raw.get('CDATE', raw.get('CALL_DATE'))
        _time_str = raw.get('CTIME', raw.get('CALL_TIME'))
        _datetime = datetime.strptime(_date_str + _time_str,
                                      "%Y%m%d%H:%M:%S")

        r = Record(interaction='call',
                   direction=direction,
                   correspondent_id=contact,
                   call_duration=float(raw['DURATION'].strip()),
                   datetime=_datetime,
                   position=position)

        return r

    with open(incoming_cdr, 'rb') as f_in:
        incoming_ = map(parse_record, csv.DictReader(f_in))

        with open(outgoing_cdr, 'rb') as f:
            outgoing_ = map(parse_record, csv.DictReader(f))

            records = itertools.chain(incoming_, outgoing_)

    name = incoming_cdr

    user = load(name, records, cells, warnings=None, describe=describe)
    return user
