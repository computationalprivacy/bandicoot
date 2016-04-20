special
========

This module contains additional features:

- functions to generate a dashboard for one user,
- routines to export indicators for deep learning tools.


dashboard
---------

This module generate an interactive dashboard to visualize user patterns.

.. image:: ../_static/bandicoot-dashboard.png

.. currentmodule:: bandicoot.special.dashboard

.. autosummary::
   :toctree: generated/

   dashboard_data
   build
   server



weekmatrix
----------

`Recent research <https://github.com/yvesalexandre/convnet-metadata>`_ shows
how deep learning methods (CNN) can achieve state-of-the-art classification
performance on mobile phone metadata. These methods can exploit the temporal
structure in mobile metadata by using specialized neural network architectures.

This module contains functions for outputting the ‘week-matrix’ data
representation, which can used with these deep learning methods. The mobile
metadata is represented as 8 matrices summarizing mobile phone usage on a
given week with hours of the day on the x-axis and the weekdays on the
y-axis. These 8 matrices are the number of unique contacts, calls, texts and
the total duration of calls for respectively incoming and outgoing
interactions. Every cell in the matrices represents the amount of activity
for a given variable of interest in that hour interval (e.g. between 2 and
3pm). In this way, any number of interactions during the week is binned.
These 8 matrices are combined into a 3-dimensional matrix with a separate
'channel' for each of the 8 variables of interest. Such a 3-dimensional
matrix is named a 'week-matrix'.

.. currentmodule:: bandicoot.special.weekmatrix

.. autosummary::
   :toctree: generated/

   create_weekmatrices
   read_csv
   to_csv
