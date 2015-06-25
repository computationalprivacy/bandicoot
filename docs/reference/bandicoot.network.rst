network
=======

.. currentmodule:: bandicoot.network

.. autosummary::
   :toctree: generated/

   matrix_index
   matrix_directed_weighted
   matrix_directed_unweighted
   matrix_undirected_weighted
   matrix_undirected_unweighted
   clustering_coefficient_unweighted
   clustering_coefficient_weighted
   assortativity_indicators
   assortativity_attributes


Matrices
--------

Networks are generated using ``User.network``, with neighbors sorted by name (see :meth:`~bandicoot.network.matrix_index` for more details).

Four different matrices can be generated:

====================== ======================================================
type                   description
====================== ======================================================
directed, weighted     Returns a directed, weighted matrix for call, text and
                       call duration. If interaction is ``None``, the weight
                       is the number of 30 minutes periods with at least one
                       call or one text.
directed, unweighted   Returns a directed, unweighted matrix where an edge
                       exists if there is at least one call or text.
undirected, weighted   Returns an undirected, weighted matrix for call, text
                       and call duration. An edge only exists if the
                       relationship is reciprocated.
undirected, unweighted Returns an undirected, unweighted matrix where an edge
                       exists if the relationship is reciprocated.
====================== ======================================================

Examples
--------

We load the demo network user from the bandicoot source directory using:

.. code-block:: python

    ego = bc.read_csv('ego', 'bandicoot/tests/samples/network')


directed, weighted
^^^^^^^^^^^^^^^^^^^

.. math::
    \begin{array}{|c|ccccccc|}
    \hline
        & ego & A & B & D & F & H \\\hline
    ego & 0   & 1 & 2 & 0 & 1 & 2 \\
    A   & 3   & 0 & 1 & 0 & 0 & 0 \\
    B   & 2   & 1 & 0 & 0 & 0 & 0 \\
    D   & 1   & 0 & 1 & / & 0 & 0 \\
    F   & 2   & 0 & 0 & 0 & 0 & 1 \\
    H   & 0   & 0 & 0 & 0 & 1 & 0 \\\hline
    \end{array}


A ``None`` cell means that we have no information of the interactions between
two users, who are both out of the network.


directed, unweighted
^^^^^^^^^^^^^^^^^^^^^

.. math::
    \begin{array}{|c|ccccccc|}
    \hline
        & ego & A & B & D & F & H \\\hline
    ego & 0   & 1 & 1 & 0 & 1 & 1 \\
    A   & 1   & 0 & 1 & 0 & 0 & 0 \\
    B   & 1   & 1 & 0 & 0 & 0 & 0 \\
    D   & 1   & 0 & 1 & / & 0 & 0 \\
    F   & 1   & 0 & 0 & 0 & 0 & 1 \\
    H   & 0   & 0 & 0 & 0 & 1 & 0 \\\hline
    \end{array}


undirected, weighted
^^^^^^^^^^^^^^^^^^^^^

.. math::
    \begin{array}{|c|ccccccc|}
    \hline
        & ego & A & B & D & F & H \\\hline
    ego & 0   & 4 & 4 & 0 & 3 & 0 \\
    A   & 4   & 0 & 2 & 0 & 0 & 0 \\
    B   & 4   & 2 & 0 & 0 & 0 & 0 \\
    D   & 0   & 0 & 0 & / & 0 & 0 \\
    F   & 3   & 0 & 0 & 0 & 0 & 2 \\
    H   & 0   & 0 & 0 & 0 & 2 & 0 \\\hline
    \end{array}


undirected, unweighted
^^^^^^^^^^^^^^^^^^^^^^^

.. math::
    \begin{array}{|c|ccccccc|}
    \hline
        & ego & A & B & D & F & H \\\hline
    ego & 0   & 1 & 1 & 0 & 1 & 0 \\
    A   & 1   & 0 & 1 & 0 & 0 & 0 \\
    B   & 1   & 1 & 0 & 0 & 0 & 0 \\
    D   & 0   & 0 & 0 & / & 0 & 0 \\
    F   & 1   & 0 & 0 & 0 & 0 & 1 \\
    H   & 0   & 0 & 0 & 0 & 1 & 0 \\\hline
    \end{array}
