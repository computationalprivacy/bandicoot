Extending bandicoot
===================


The user object
---------------

The :class:`~bandicoot.core.User` object is composed of a list of records and, optionally, a dictionary of attributes.

Records
^^^^^^^

A record is stored in the class :class:`~bandicoot.core.Record`:

================ ================================ ========================================================================================
name             type                             description
================ ================================ ========================================================================================
interaction      string [required]                ``'call'``, ``'text'``
direction        string                           whether the user was called/texted (``'in'``) or was the one calling/texting (``'out'``)
correspondent_id string                           identifier of the correspondent
datetime         datetime                         timestamp of the record
call_duration    interaction                      duration of the call in seconds or ``None`` for texts
position         :meth:`~bandicoot.core.Position` a position object ``Position(antenna=13084)``
================ ================================ ========================================================================================

Records are stored as a list, and can be accessed or modified with
the property :meth:`User.records <bandicoot.core.User.records>`.

User attributes
^^^^^^^^^^^^^^^

User attributes are loaded at the same time as the records. Attributes are
stored in a dictionary that can be access by :meth:`User.attributes
<bandicoot.core.User.attributes>`: ::

        >>> user.attributes['age'] = 42
        >>> user.attributes['likes_trains'] = True


Object attributes
^^^^^^^^^^^^^^^^^

Object attributes are created by bandicoot when the user's records are loaded:

=================== ======== ===================================================
keys                type     description
=================== ======== ===================================================
has_call            bool     whether call records have been loaded
has_text            bool     whether text records have been loaded
has_antennas        bool     whether antennas have been loaded
has_recharges       bool     whether recharges have been loaded
has_gps             bool     whether gps locations have been loaded
start_time          datetime time of the first record
end_time            datetime time of the last record
antennas            dict     dictionary of antennas with antenna_id as keys
                             and latlon tuples
home                string   the position (antenna id) the user spends the most time at
                             during the night. Computed using
                             :meth:`~bandicoot.core.User.recompute_home()`
=================== ======== ===================================================


.. _new-indicator-label:

Writing a new indicator
-----------------------

A lot of the complexity of bandicoot is hidden from the user when writing a new indicator. For example, let's look at the method :meth:`~bandicoot.individual.balance_of_contacts`:

.. code-block:: python

    from bandicoot.helper.maths import summary_stats

    @grouping
    def balance_of_contacts(records):
        """
        Computes the balance of all interactions. For every tie, the balance is the
        number of outgoing interactions divided by the total number of interactions.
        """

        counter_out = defaultdict(int)
        counter = defaultdict(int)

        for r in records:
            if r.direction == 'out':
                counter_out[r.correspondent_id] += 1
            counter[r.correspondent_id] += 1

        balance = [float(counter_out[c]) / float(counter[c]) for c in counter]

        return summary_stats(balance)


bandicoot's ``@grouping`` `decorator` manages the ``interaction`` and ``groupby`` keywords for you. It selects the right records (e.g. only calls) and groups them (e.g. by week). By default ``interaction=['call','text']`` but this can be redefined in the decorator ``@grouping(interaction='call')``. The function ``balance_of_contacts`` is then called for each group of records and the results are combined.

In this function, ``records`` is thus a subset of ``B.records`` (e.g. only the calls in a specific week). ``records`` is equal to ``B.records`` if the function is called with ``groupby='week'`` and ``interaction=['callandtext']``.


.. note:: The function executes the following operations:

  1. First, we initialize two empty ``int`` dictionaries using ``defaultdict`` from the collections module.
  2. The ``for`` loop then goes over each record passed by the `decorator`. It counts the total number of interactions and the number of outgoing interactions per contacts.
  3. We then compute, for each contact, the balance of interactions. Note that ``counter_out`` is a defaultdict, and ``counter_out[c]`` will return 0 even if ``c`` is not in the dictionary.
  4. `balance` is a list of the balance of interaction with each contact. We thus pass it to bandicoot's :meth:`~bandicoot.helper.tools.summary_stats` which will return the mean and std if ``summary=default``; the mean, std, median, min, max, kurtosis, skewness if ``summary=extended``; and the full distribution if ``summary=None``.


Indicators using ``@grouping`` can return either a number (simply return the value) or a distribution (by calling summary_stats as shown); bandicoot automatically takes both values into account. For example, :meth:`~bandicoot.individual.number_of_contacts` returns only one number.


Accessing the User object
^^^^^^^^^^^^^^^^^^^^^^^^^

A function to compute a new indicator might need to access more than just the list of records. A function might, for example, need to be able to access the GPS coordinate of an antenna or the first record we have available for this user. The method can ask the decorator to also pass the full user object using ``@grouping(user_kwd=True)``. It can then access all the records (`user.records`), the list of antennas (`user.antennas`), or other properties (see Object attributes).

.. code-block:: python

  @grouping(user_kwd=True)
  def my_indicator(records, user):
    pass


Integrating your indicator
^^^^^^^^^^^^^^^^^^^^^^^^^^

First, add it to bandicoot's test suite. bandicoot puts a strong emphasis on the correctness and consistency of its indicators. We thus require the values to be manually computed for the sample users located in ``bandicoot/tests/samples/manual/``. These manually computed value can then be added to the JSON file also located in ``bandicoot/tests/samples/manual/`` and tested using:

.. code-block:: bash

  nosetests -w bandicoot/tests -v


The new metric can be integrated to the default bandicoot pipeline by adding it to :meth:`~bandicoot.utils.all`.


Testing
-------

To run the unit tests with `nose`_, use the following command:

.. _nose : https://nose.readthedocs.org

.. code-block:: bash

  nosetests -w bandicoot/tests -v

Note that running the tests requires additional modules such as `nose`, `numpy`, `scipy`, and `networkx`.

