Using bandicoot
===============

More information on the getting started with bandicoot can be found in the :doc:`../quickstart`

Indicators
^^^^^^^^^^

bandicoot indicators are divided in three modules (:mod:`~bandicoot.individual`, :mod:`~bandicoot.spatial`, and :mod:`~bandicoot.network`).

.. autosummary::

   bandicoot.individual.active_days
   bandicoot.individual.number_of_contacts
   bandicoot.individual.number_of_interactions
   bandicoot.individual.call_duration
   bandicoot.individual.percent_nocturnal
   bandicoot.individual.percent_initiated_conversation
   bandicoot.individual.percent_initiated_interactions
   bandicoot.individual.response_delay_text
   bandicoot.individual.response_rate_text
   bandicoot.individual.entropy_of_contacts
   bandicoot.individual.interactions_per_contact
   bandicoot.individual.interevents_time
   bandicoot.spatial.number_of_places
   bandicoot.spatial.entropy_places
   bandicoot.spatial.percent_at_home
   bandicoot.spatial.radius_of_gyration
   bandicoot.network.clustering_coefficient



They can also be computed at once using :meth:`bandicoot.utils.all`.

Loading data and exporting indicators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:meth:`~bandicoot.io.read_csv` is the standard way to load users. bandicoot can also load *single* users (without their network) though
:meth:`~bandicoot.io.load` or other csv formats such as
:meth:`~bandicoot.io.read_orange` or :meth:`~bandicoot.io.read_telenor`.


.. autosummary::

   bandicoot.io.load
   bandicoot.io.read_csv
   bandicoot.io.read_orange
   bandicoot.io.read_telenor
   bandicoot.io.to_csv
   bandicoot.io.to_json

Attributes
----------

.. warning::

   Attributes are currently loaded in the :class:`~bandicoot.core.User` class, but
   not used by any implemented metric.

The attribute file is an optional file that contains information about the individual.
This information can, for example, be used to compute the ego-network assortativity or clustering coefficient.
Any attribute can be loaded and values can be ``string``, ``int``, or ``float``.
bandicoot predefines a few keys such as individual_id, gender, or subscriber.

============= ============
key           value
============= ============
individual_id 7atr8f53fg41
gender        male
is_subscriber True
age           42
============= ============

It can be loaded as a csv, with the following header
::

  key,value
  individual_id,7atr8f53fg41
  gender,male
  is_subscriber,True
  age,42

Attributes are optional and can be loaded at the same time as the records using
:meth:`~bandicoot.io.read_csv`.

>>> B = bc.read_csv('my_user', 'records/', 'antennas.csv', attributes_path='attributes/')



Arguments
^^^^^^^^^

Summary
-------

As described in the :doc:`quickstart`, bandicoot returns by default the mean and std or the value of indicators.

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

Interaction
-----------

The :mod:`bandicoot.individual` and :mod:`bandicoot.network` indicators can be computed on ``call``, ``text``, or ``callandtext``.

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


.. _conversations-label:

Conversations
^^^^^^^^^^^^^

Some bandicoot indicators rely on texts being grouped into conversations (see :mod:`~bandicoot.individual`). We define conversations as a series of text messages between the user and one contact. A conversation starts with either of the parties sending a text to the other. A conversation will stop if no text was exchanged by the parties for an hour or if one of the parties call the other. The next conversation will start as soon as a new text is send by either of the parties.


Exemple
-------

- At 10:00, Alice sends a message to Bob “*Where are you? I'm waiting at the train station. I have your ice cream.*”
- At 10:01, Bob responds with a text “*I'm running late, I should be there soon.*”
- At 10:05, Bob sends another message “*I missed my bus :(*”
- At 10:10, Alice calls Bob to tell him she eated the ice cream and took the train.

The first three text messages define a conversation between Alice and Bob, which is ended by the last call. The call is not included in the conversation.

The distribution of delays is *[60 seconds, 240 seconds]*. Bob's response rate is *1* as he responded to Alice first message.


.. note::

   A conversation can be defined by just one text message. In this case, the response delay is ``None``.

