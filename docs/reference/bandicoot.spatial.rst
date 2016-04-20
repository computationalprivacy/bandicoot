spatial
=======

This module contains indicators from user location and movement patterns,
during active as well as passive usage of mobile phone. Location is reported
from mobile phone antennas (cell towers) and GPS records if provided.


.. warning::

	These functions use spatial binning; for every half-hour, interactions are binned.
	The most common location for the binned records is used as the user's location for that half-hour.


.. currentmodule:: bandicoot.spatial

.. autosummary::
   :toctree: generated/

   number_of_antennas
   entropy_of_antennas
   percent_at_home
   radius_of_gyration
   frequent_antennas
   churn_rate
