core classes
============

.. currentmodule:: bandicoot


The ``core`` module contains classes to store all the data used by bandicoot.


User
----

.. autosummary::
   :toctree: generated/

   User

Attributes and underlying data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   
   User.records
   User.antennas
   User.recharges
   User.attributes
   User.network
   User.home

   User.has_antennas
   User.has_recharges
   User.has_attributes
   User.has_network
   User.has_home

   User.name
   User.antennas_path
   User.attributes_path
   User.recharges_path

   User.start_time
   User.end_time
   User.night_start
   User.night_end
   User.start_time
   User.weekend

   User.ignored_records

   User.percent_outofnetwork_calls
   User.percent_outofnetwork_texts
   User.percent_outofnetwork_contacts
   User.percent_outofnetwork_call_durations


Methods
~~~~~~~

.. autosummary::
   :toctree: generated/

   User.describe
   User.recompute_home
   User.recompute_missing_neighbors
   User.reset_cache
   User.set_home


Record
------

.. autosummary::
   :toctree: generated/

   Record

Attributes and underlying data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   Record.interaction
   Record.direction
   Record.correspondent_id
   Record.datetime
   Record.call_duration
   Record.position

Methods
~~~~~~~

.. autosummary::
   :toctree: generated/

   Record.matches
   Record.all_matches
   Record.has_match


Position
--------

.. autosummary::
   :toctree: generated/

   Position

Attributes and underlying data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   Position.location
   Position.antenna

Methods
~~~~~~~

.. autosummary::
   :toctree: generated/

   Position.type


Recharge
--------

.. autosummary::
   :toctree: generated/

   Recharge

Attributes and underlying data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   Recharge.datetime
   Recharge.amount
   Recharge.retailer_id
