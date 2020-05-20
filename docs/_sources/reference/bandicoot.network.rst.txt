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

We load the following examples using the network user from the bandicoot source directory using:

.. code-block:: python

    >>> ego = bc.read_csv('ego', 'bandicoot/tests/samples/network', network=True)


directed, weighted
^^^^^^^^^^^^^^^^^^^

:meth:`~bandicoot.network.matrix_directed_weighted` returns a directed,
weighted matrix for call, text and call duration. By default, interaction is
``None``: the weight is the number of 30 minutes periods with at least one
call or one text. Summing call and texts is not accurate, counting periods of
activity leads to a better understanding of the interactions.


.. code-block:: python

    >>> bc.network.matrix_index(ego)
    ['ego', 'A', 'B', 'D', 'F', 'H']

    >>> m = bc.network.matrix_directed_weighted(ego)
    >>> m

    [[0, 3, 2, 1, 2, 0],
     [1, 0, 1, 0, 0, 0],
     [2, 1, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 1],
     [0, 0, 0, 0, 1, 0]]


The cell ``m[0][1]``, equal to 3, is the number of interactions from ego (index 0) to
A (index 1).

A ``None`` cell means that we have no information of the interactions between
two users, who are both out of the network.


directed, unweighted
^^^^^^^^^^^^^^^^^^^^^

:meth:`~bandicoot.network.matrix_directed_unweighted` returns a directed,
unweighted matrix where an edge exists if there is at least one call or text,
in both direction.

.. code-block:: python

    >>> bc.network.matrix_directed_unweighted(ego)

    [[0, 1, 1, 1, 1, 0],
     [1, 0, 1, 0, 0, 0],
     [1, 1, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 1],
     [0, 0, 0, 0, 1, 0]]


undirected, weighted
^^^^^^^^^^^^^^^^^^^^^

:meth:`~bandicoot.network.matrix_undirected_weighted` returns an undirected,
weighted matrix for call, text and call duration. An edge only exists if the
relationship is reciprocated. It counts the total number of interactions in
both directions.

.. code-block:: python

    >>> bc.network.matrix_undirected_weighted(ego)

    [[0, 4, 4, 0, 3, 0],
     [4, 0, 2, 0, 0, 0],
     [4, 2, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [3, 0, 0, 0, 0, 2],
     [0, 0, 0, 0, 2, 0]]


undirected, unweighted
^^^^^^^^^^^^^^^^^^^^^^^

:meth:`~bandicoot.network.matrix_undirected_unweighted` returns an undirected,
unweighted matrix where an edge exists if the relationship is reciprocated.

.. code-block:: python

    >>> bc.network.matrix_undirected_unweighted(ego)

    [[0, 1, 1, 0, 1, 0],
     [1, 0, 1, 0, 0, 0],
     [1, 1, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 1],
     [0, 0, 0, 0, 1, 0]]