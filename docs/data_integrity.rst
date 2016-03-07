Data integrity
==============


Collecting mobile phone metadata can lead to corrupted data: wrong format, faulty files, empty periods of time or missing users, *etc.* bandicoot will not try to fix corrupted data, but however let you handle such situations by:

1. warning you when importing data,
2. removing faulty records,
3. adding more than 30 reporting variables when exporting indicators.



Warnings at import
------------------

By default, :meth:`~bandicoot.io.read_csv` logs six warnings to the standard output:

1. when an attribute path is given, but no attributes are loaded (which can occur when the path is wrong, or the attribute file empty),
2. a recharges path given, but no recharges loaded,
3. the percentage of records missing a location when positive,
4. the number of antennas missing a location (when an antenna file was provided)
5. the percentage of duplicated records (which can happen when databases are mixed together)
6. the percentage of calls with an overlap of more than 5 minutes


Removal of faulty records
-------------------------

When loading a CSV file containing records, bandicoot filters out lines with wrong values, and keeps the count of ignored lines in the :class:`~bandicoot.core.User` object:

.. code-block:: python

	>>> my_user.ignored_records
	{'all': 5,
	 'call_duration': 3,
	 'correspondent_id': 0,
	 'datetime': 2,
	 'direction': 4,
	 'interaction': 0,
	 'location': 0}

The previous example means that six records were removed because:

- three records had wrong call durations,
- two records had wrong dates and times,
- four records had wrong with directions.

.. warning:: An ignored record with multiple faulty fields will be counted for all field, and not only for the first detected. The sum of all ignored fields in ``my_user.ignored_records`` is not equal to 5, the number of ignored records.


bandicoot can also remove duplicated records, if the option ``drop_duplicates=True`` is provided to :meth:`bandicoot.core.read_csv`. This functionality is not activated by default, as one user can send multiple text messages in less than one minute (or less, depending on the granularity of the data set), yet they should not count as duplicated.

Reporting variables
-------------------

The function :meth:`~bandicoot.utils.all` returns a nested dictionnary containing all indicators, but also 31 reporting variables:

1. concerning the data loading (``antennas_path``, ``attributes_path``, ``recharges_path``),
2. about the user (``start_time``, ``end_time``, ``night_start``, ``night_end``, ``weekend`` with a list of days defining a weekend, ``number_of_records``, ``number_of_antennas``, ``number_of_recharges``, ``bins``, ``bins_with_data``, ``bins_without_data``, ``has_call``, ``has_home``, ``has_recharges``, ``has_attributes``, ``has_network``),
3. on records missing information (``percent_records_missing_location``, ``antennas_missing_locations``, and ``ignored_records`` mentioned previously),
4. on the user's ego network (``percent_outofnetwork_calls``, ``percent_outofnetwork_texts``, ``percent_outofnetwork_contacts``, ``percent_outofnetwork_call_durations``),
5. on the computation (``groupby``, ``split_week``, ``split_day``).
