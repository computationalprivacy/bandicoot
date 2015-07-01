Using bandicoot
===============

bandicoot indicators are divided in three modules (:doc:`reference/bandicoot.individual`, :doc:`reference/bandicoot.spatial`, and :doc:`reference/bandicoot.network`).

They can also be computed at once using :meth:`bandicoot.utils.all`. :doc:`reference/bandicoot.network` indicators will only be returned if the user was loaded in :meth:`~bandicoot.io.read_csv` using `network=True`.


Summary
-------

As described in :doc:`quickstart`, bandicoot returns by default the mean and std or the value of indicators.


When the indicator is a timeseries, for example in the case of
:meth:`~bandicoot.individual.call_duration`, bandicoot can also return the
median, min, max, kurtosis, and skewness using ``summary=extended`` or the full
timeserie using ``summary=None``. Note that, by default, bandicoot returns a list of lists with one list for every week.

  >>> bc.individual.call_duration(B, summary='extended')
  'call': {'kurtosis': {'mean': 1.7387436274109511, 'std': 0.5453153466587801},
          'max': {'mean': 839.1310344827587, 'std': 171.05797586147924},
          'mean': {'mean': 509.85158868177155, 'std': 133.02496554053093},
          'median': {'mean': 511.11034482758623, 'std': 169.27744486865464},
          'min': {'mean': 172.02068965517242, 'std': 175.2274765482155},
          'skewness': {'mean': -0.03923002617046248, 'std': 0.472380180345131},
          'std': {'mean': 238.69736346741757, 'std': 85.48627089424896}}}


  >>> bc.individual.call_duration(B, summary=None)
  {'call': [[686],[20, 192, 345, 470, 530, 983],[195, 284, 469, 672],...]}

  >>> bc.individual.call_duration(B, summary=None, groupby=None)
  {'call': [7, 7, 7, 7, 7, 8, 14, 15, 15, 16, 17, 17]}


=============== ============ ===============================================
summary         single value timeserie
=============== ============ ===============================================
default          value       mean, std
extended         value       mean, std, median, min, max, kurtosis, skewness
None             value       the full distribution
=============== ============ ===============================================

Interaction type
----------------

The :doc:`reference/bandicoot.individual` and :doc:`reference/bandicoot.network` indicators can be computed on records of type ``call``, ``text``, or ``callandtext`` (which includes both calls and texts).

For example, :meth:`~bandicoot.individual.active_days` returns, by default, the
number of days a user has been active overall::

   >>> bc.individual.active_days(B)
   {'callandtext': {'mean': 5.517241379310345, 'std': 1.6192950713019956}}

This behavior can be changed using the ``interaction`` keyword which takes a list::

   >>> bc.individual.active_days(B, interaction=['callandtext','call','text'])
   {'call': {'mean': 4.124137931034483, 'std': 1.639523726556146},
   'callandtext': {'mean': 5.517241379310345, 'std': 1.6192950713019956},
   'text': {'mean': 4.253521126760563, 'std': 1.611737841360057}}

If an interaction type is specified and there are no records of that type, bandicoot will return ``None`` for that indicator::

    >>> B.has_text
    False
    >>> bc.individual.number_of_contacts(B, interaction=['call','text'])
    {'text': None, 'call': {'mean': 15.2, 'std': 0.32}}


Splits (days and hours)
-----------------------

* ``split_week=True`` causes records from weekdays and weekends to be considered separately and reported along with the allweek values.
* ``split_day=True`` causes records from daytime and nightime to be considered separately and reported along with the allday values.

(By default, "night" is defined as 7 p.m. to 7 a.m.)

    >>> bc.individual.active_days(ego, split_week=True)
    {'allweek': {'allday': {'callandtext': {'mean': 5.5,
         'std': 2.598076211353316}}},
     'weekday': {'allday': {'callandtext': {'mean': 4.428571428571429,
         'std': 1.3997084244475304}}},
     'weekend': {'allday': {'callandtext': {'mean': 1.8571428571428572,
         'std': 0.34992710611188266}}}}

This output implies that ego is active approximately 1.86 days each weekend and 4.43 days each week.