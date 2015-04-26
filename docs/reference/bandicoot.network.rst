network
=======

.. currentmodule:: bandicoot.network

.. autosummary::
   :toctree: generated/

   clustering_coefficient


Networks are generated using User.network, with neighbors sorted by key (``neighbors = [user.name] + sorted([k for k in user.network.keys() if k != user.name])``).

Four different matrices can be generated:
======================== ===================================================
type     				 description
======================== ===================================================
directed, weighted	     Returns a directed, weighted matrix for call, text and call duration.
   						 If interaction is None the weight is the sum of the number of calls and texts.
directed, unweighted     Returns a directed, unweighted matrix where an edge exists if there is at least one call or text.
undirected, weighted     Returns an undirected, weighted matrix for call, text and call duration.
				         An edge only exists if the relationship is reciprocated.
undirected, unweighted   Returns an undirected, unweighted matrix where an edge exists if the relationship is reciprocated.

The matrices are all ordered ego + other keys sorted.

Examples
--------
sample network user (/bandicoot/tests/samples/network)

directed, weighted
^^^^^^^^^^^^^^^^^^^

	 ego  A  B  D  F  H
	 -------------------
ego | 0   1  2  0  1  2
A   | 3   0  0  0  0  0
B   | 2   0  0  0  0  0
D   | 1   Na 1  Na Na Na
F   | 2   0  0  0  0  1
H   | 1   0  0  0  1  0


directed, unweighted
^^^^^^^^^^^^^^^^^^^^^

	 ego  A  B  D  F  H
	 -------------------
ego | 0   1  1  0  1  1
A   | 1   0  0  0  0  0
B   | 1   0  0  0  0  0
D   | 1   Na 1  Na Na Na
F   | 1   0  0  0  0  1
H   | 1   0  0  0  1  0


undirected, weighted
^^^^^^^^^^^^^^^^^^^^^

	 ego  A  B  D  F  H
	 -------------------
ego | 0   4  4  0  3  3
A   | 4   0  0  0  0  0
B   | 4   0  0  0  0  0
D   | Na  Na Na  Na Na Na
F   | 3   0  0  0  0  2
H   | 3   0  0  0  2  0


undirected, unweighted
^^^^^^^^^^^^^^^^^^^^^^^

	 ego  A  B  D  F  H
	 -------------------
ego | 0   1  1  0  1  1
A   | 1   0  0  0  0  0
B   | 1   0  0  0  0  0
D   | Na  Na Na  Na Na Na
F   | 1   0  0  0  0  1
H   | 1   0  0  0  1  0

