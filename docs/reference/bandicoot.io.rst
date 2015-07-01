IO
==


:meth:`~bandicoot.io.read_csv` is the standard way to load users. bandicoot can also load users though
:meth:`~bandicoot.io.load` (low-level function, called by :meth:`~bandicoot.io.read_csv`) or other CSV formats such as
:meth:`~bandicoot.io.read_orange` or :meth:`~bandicoot.io.read_telenor` (deprecated).


.. currentmodule:: bandicoot.io

.. autosummary::
   :toctree: generated/

   read_csv
   read_orange
   read_telenor
   to_csv
   to_json
   load
   filter_record


.. _attributes-label:

Attributes
----------

The attribute file is an optional file that contains information about the individual.
This information can, for example, be used to compute the ego-network :meth:`~bandicoot.network.assortativity_attributes`.
Any attribute can be loaded and values can be ``string``, ``int``, or ``float``.
bandicoot predefines a few keys such as individual_id, or gender.

============= ============
key           value
============= ============
individual_id 7atr8f53fg41
gender        male
age           42
============= ============

It can be loaded as a CSV, with the following header
::

  key,value
  individual_id,7atr8f53fg41
  gender,male
  age,42

Attributes are optional and can be loaded at the same time as the records using
:meth:`~bandicoot.io.read_csv`.

>>> B = bc.read_csv('my_user', 'records/', 'antennas.csv', attributes_path='attributes/')
