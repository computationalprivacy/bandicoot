Extending bandicoot
===================


The user object
---------------

The user object is composed of a list of records, a dictionary of attributes,
and object's attributes.

Records
^^^^^^^

A record is stored as a named tuple by the class :class:`~bandicoot.core.Record`:

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

User's records are stored as a list, and can be accessed or modified with
the property :meth:`User.records <bandicoot.core.User.records>`.

User attributes
^^^^^^^^^^^^^^^

User attributes can be loaded at the same time as his records. Attributes are
stored in a dictionary that can be access by :meth:`User.attributes
<bandicoot.core.User.attributes>`: ::

        >>> user.attributes['age'] = 42
        >>> user.attributes['likes_trains'] = True

bandicoot has reserved names for a few attributes:

============= ====== =====================================
keys          type   description
============= ====== =====================================
individual_id string the user identifier, required for networked users
gender        string can be ``male`` or ``female``
age           int    age of the user
============= ====== =====================================

Object attributes
^^^^^^^^^^^^^^^^^

Object's attributes are created by bandicoot when the user's records are loaded:

=================== ======== ===================================================
keys                type     description
=================== ======== ===================================================
has_call            bool     whether call records have been loaded
has_text            bool     whether text records have been loaded
has_antennas        bool     whether antennas have been loaded
has_gps             bool     whether gps locations have been loaded
start_time          datetime time of the first record
end_time            datetime time of the last record
places              dict     dictionary of places with place_id as keys
                             and latlon tuples
home                string   the position the user spends the most time at
                             during the night. Computed using
                             :meth:`~bandicoot.core.User.recompute_home()`
=================== ======== ===================================================


.. _new-indicator-label:

Writing a new indicator
-----------------------

A lot of the complexity of bandicoot is hidden from the user when writing a new indicator. For example, let's look at the method :meth:`~bandicoot.individual.balance_interaction`:

.. code-block:: python

    @grouping
    def balance_interaction(records):
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

        return summary_stats(balance, 0.99)


bandicoot's ``@grouping`` `decorator` manages the ``interaction`` and ``groupby`` keywords for you. It selects the right records (e.g. only calls) and group them (e.g. per week). By default ``interaction=['call','text']`` but this can be redefined in the decorator ``@grouping(interaction='call')``. The function ``balance_interaction`` is then called for each group of records and the results are combined. 

In this function, ``records`` is thus a subset of ``B.records`` (e.g. only the calls in a specific week). ``records`` is equal to ``B.records`` if the function is called with ``groupby='week'`` and ``interaction=['callandtext']``. 

1. First, we initialize two empty ``int`` dictionaries using ``defaultdict`` from the collections module.
2. The ``for`` loop then goes over all the records passed by the `decorator`. It counts the total number of interactions and the number of outgoing interactions per contacts. 
3. We then compute, for each contact, the balance of interaction. Note that ``counter_out`` is a defaultdict, and ``counter_out[c]`` will return 0 even if c is not in the dictionnary.
4. `balance` is a list of the balance of interaction with each contact. We thus pass it to bandicoot's :meth:`~bandicoot.helper.tools.summary_stats` which will return the mean and std if ``summary=default``; the mean, std, median, min, max, kurtosis, skewness if ``summary=extended``; and the full distribution if ``summary=None``.


Indicators using ``@grouping`` can return either one number or a distribution; bandicoot automatically takes both values into account. For example, :meth:`~bandicoot.individual.number_of_contacts` returns only one number.


Accessing the user object
^^^^^^^^^^^^^^^^^^^^^^^^^

A function to compute a new indicator might need to access more than just the list of records. A function might, for example, need to be able to access the GPS coordinate of an antenna or the first record we have available for this user. The method can ask the decorator to pass the full user object using ``@grouping(user_kwd=True)``. It can then access all the records (`user.records`), the list of antennas (`user.antenna`), or other properties (see Object attributes).

Integrating your indicator
^^^^^^^^^^^^^^^^^^^^^^^^^^

First, add it to bandicoot's test suite. bandicoot puts a strong emphasis on the correctness and consistency of its indicators. We thus require the values to be manually computed for the sample users located in `` bandicoot/tests/samples/manual/``. These manually computed value can then be added to the JSON file also located in `` bandicoot/tests/samples/manual/`` and tested using::

.. code-block:: bash
  
  nosetests -w bandicoot/tests -v


The new metric can be integrated to the default bandicoot pipeline by adding it to :meth:`~bandicoot.utils.all`.


Testing
-------

To run the unit tests with `nose`_, use the following command:

.. _nose : https://nose.readthedocs.org

.. code-block:: bash
  
  nosetests -w bandicoot/tests -v

Note that running the tests requires additionnal modules such as `nose`, `numpy`, and `scipy`.


Testing layout
^^^^^^^^^^^^^^
bandicoot's testing suite is laid out as follows:

================== ========================================================================================================
file name          purpose
================== ========================================================================================================
test_automatic.py  Tests the idempotency of bandicoot's metrics on an automatically generated user.
test_core.py       Tests the functionality of bandicoot's main objects.
test_export.py     Tests the functionality of bandicoot's file writing methods.
test_group.py      Tests the functionality of bandicoot's aggregation methods and the statistics that come out as a result.
test_manual.py     Tests a suite of manually crafted users for edge cases.
test_parsers.py    Tests the read_XYZ methods.
test_sequences.py  Tests the functionality of bandicoot's interevents.
test_utils.py      Tests the correctness of bandicoot's utility methods.
================== ========================================================================================================


Fixture layout
^^^^^^^^^^^^^^
bandicoot comes with a few sets of fixture data. These may be found inside
the directory ``bandicoot/tests/samples``.

=========================================== ========================================================================================================
file name                                   representation
=========================================== ========================================================================================================
automatic/automatic_result.csv              The csv produced by writing the automatic user to CSV.
automatic/automatic_result.json             The json produced by writing the automatic user to JSON.
automatic/automatic_result_extended.json    The json produced when producing an extended summary on the automatic user.
automatic/automatic_result_no_grouping.json The json produced when there is no aggregation performed on the automatic user.
automatic/automatic_user.csv                The csv representing a month's worth of user records.
orange/orange_result.csv                    The csv produced by writing the Orange user to CSV.
orange/orange_result.json                   The json produced by writing the Orange user to JSON.
orange/orange_user.csv                      The automatic user in Orange format.
telenor/cells.csv                           The cells needed for the Telenor format.
telenor/incoming.csv                        The incoming records for the user in Telenor format.
telenor/outgoing.csv                        The outgoing records the user in Telenor format.
telenor/telenor_result.csv                  The csv produced by writing the Telenor user to CSV.
telenor/telenor_result.json                 The json produced by writing the Telenor user to JSON.
attributes.csv                              A set of attributes for a user.
empty_user.json                             The json object produced on an empty user with no records.
to_csv_different_keys.csv                   The csv produced when records do not have the same set of keys.
to_csv_same_keys.csv                        The csv produced when records do have the same set of keys.
to_csv_different_keys.json                  The json produced when records do not have the same set of keys.
to_csv_same_keys.json                       The json when records do have the same set of keys.
towers.csv                                  An sample antenna file.
towers.json                                 The sample antenna file in JSON format (to be loaded as a dictionary).
=========================================== ========================================================================================================

