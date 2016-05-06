Data integrity
==============


Occasionally, records in CDR and collected mobile phone metadata can be
corrupted: wrong format, faulty files, empty periods of time, missing users,
*etc.* bandicoot will not attempt to correct errors as this might lead to
incorrect analysis. It will instead:

1. warn you when you attempt to import corrupted data, 
2. remove faulty records, 
3. report more than 30 variables warning you of potential issues when exporting
   indicators. 



Warnings at import
------------------

By default, :meth:`~bandicoot.io.read_csv` reports six warnings to the standard output:

1. when an *attribute path* is given but no attributes could be loaded, e.g.
   because the path is wrong or because the attribute file is empty, 
2. when a *recharges_path* is given but no recharges could be loaded, 
3. the percentage of records that do not contain location informationwhen an
   antenna file is provided, the number of antennas missing location information
4. the percentage of duplicated records
5. the percentage of calls with an overlap of more than 5 minutes 


Removal of faulty records
-------------------------

bandicoot will automatically remove faulty records and will report the number
of ignored records (also available in the :class:`~bandicoot.core.User` Object):

.. code-block:: python

	>>> my_user.ignored_records
	{'all': 5,
	 'call_duration': 3,
	 'correspondent_id': 0,
	 'datetime': 2,
	 'direction': 4,
	 'interaction': 0,
	 'location': 0}

In this example, six records were removed:

- three records had incorrect call durations,
- two records had incorrect dates and times,
- four records had incorrect incoming or outgoing directions.

.. warning:: An ignored record with multiple faulty fields will be double
   counted and reported for each incorrect value. The total number of ignored
   records is reported in all, here 5.


bandicoot also offer the option to remove “duplicated records“ (same
correspondants, direction, date and time). The option ``drop_duplicates=True``
in :meth:`~bandicoot.io.read_csv` is not activated by defaul, as one user
might send multiple text messages in less than one minute (or less, depending
on the granularity of the data set).

Reporting variables
-------------------

The function :meth:`~bandicoot.utils.all` returns a nested dictionary containing all indicators, but also 39 reporting variables:

1. information on the files: ``antennas_path``, ``attributes_path``, ``recharges_path``,
2. information about the data: ``start_time``, ``end_time``, ``night_start``, ``night_end``, ``weekend`` with a list of days defining a weekend, ``number_of_records``, ``number_of_antennas``, ``number_of_recharges``…,
3. information on records for which information is missing: ``percent_records_missing_location``, ``antennas_missing_locations``, and ``ignored_records`` mentioned previously,
4. information on the user's ego network: ``percent_outofnetwork_calls``, ``percent_outofnetwork_texts``, ``percent_outofnetwork_contacts``, ``percent_outofnetwork_call_durations``,
5. and finally, information on the grouping: ``groupby``, ``split_week``, ``split_day``.
