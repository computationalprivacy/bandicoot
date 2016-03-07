core
====

.. currentmodule:: bandicoot.core


User class
----------

.. autoclass:: bandicoot.core.User
   :members:


Record class
------------

.. autoclass:: bandicoot.core.Record
   :members:


Position class
--------------

.. autoclass:: bandicoot.core.Position
   :members:

   .. attribute:: antenna

   	  A unique identifier of the antenna

   .. attribute:: position

      A tuple (lat, lon) with the latitude and longitude of the antenna,
      encoded as floating point numbers.


Recharge class
--------------

.. autoclass:: bandicoot.core.Recharge
   :members:

   .. attribute:: datetime

   	  A datetime object with the date and time of the transaction.

   .. attribute:: amount

   	  The total amount recharged.

   .. attribute:: retailer_id

   	  A unique identifier of the retailer for the transaction.
