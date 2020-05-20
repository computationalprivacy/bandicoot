utils and helper
================


utils
-----

.. currentmodule:: bandicoot.utils

.. autosummary::
   :toctree: generated/

   all
   flatten


helper.group
------------

.. currentmodule:: bandicoot.helper.group
.. autosummary::
   :toctree: generated/

   filter_user
   positions_binning
   group_records_with_padding
   group_records
   infer_type
   statistics
   grouping
   spatial_grouping
   recharges_grouping



helper.tools
------------

.. currentmodule:: bandicoot.helper.tools
.. autosummary::
   :toctree: generated/

   CustomEncoder
   OrderedDict
   advanced_wrap
   Colors
   ColorHandler
   percent_records_missing_location
   percent_overlapping_calls
   antennas_missing_locations
   pairwise
   AutoVivification


helper.maths
------------

.. currentmodule:: bandicoot.helper.maths
.. autosummary::
   :toctree: generated/

   mean
   kurtosis
   skewness
   std
   moment
   median
   minimum
   maximum
   SummaryStats
   summary_stats
   entropy
   great_circle_distance


helper.stops
------------

Building spatial indicators with both coarse (cell towers) and fine-grained
(GPS) positions is not trivial. This modules helps cluster GPS locations and
update the positions of given records to the closest cluster:

1. :meth:`~bandicoot.helper.stops.cluster_and_update` clusters records and updates
   their location,
2. :meth:`~bandicoot.helper.stops.fix_location` updates the position of all records
   based on closest cluster found, to avoid having both antennas from cell towers
   and from clusters.

Algorithms implemented in this module were designed by Andrea Cuttone [CUT2013]_.

.. currentmodule:: bandicoot.helper.stops
.. autosummary::
   :toctree: generated/

   cluster_and_update
   fix_location
   compute_distance_matrix

**Low-level functions**

.. currentmodule:: bandicoot.helper.stops
.. autosummary::
   :toctree: generated/

   dbscan
   get_neighbors
   get_stops

**References**

.. [CUT2013] Cuttone, A. (2013). SensibleJournal: A Mobile Personal Informatics
    System for Visualizing Mobility and Social Interactions. ISO 690  
