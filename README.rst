=========
bandicoot
=========

.. image:: https://img.shields.io/pypi/v/bandicoot.svg
    :target: https://pypi.python.org/pypi/bandicoot
    :alt: Version
     
.. image:: https://img.shields.io/pypi/l/bandicoot.svg
    :target: https://github.com/yvesalexandre/bandicoot/blob/master/LICENSE
    :alt: MIT License

.. image:: https://img.shields.io/pypi/dm/bandicoot.svg
    :target: https://pypi.python.org/pypi/bandicoot
    :alt: PyPI downloads

.. image:: https://img.shields.io/travis/yvesalexandre/bandicoot.svg
    :target: https://travis-ci.org/yvesalexandre/bandicoot
    :alt: Continuous integration

.. begin

**bandicoot** (http://bandicoot.mit.edu) is Python toolbox to analyze mobile phone metadata. It provides a complete, easy-to-use environment for data-scientist to analyze mobile phone metadata. With only a few lines of code, load your datasets, visualize the data, perform analyses, and export the results.

.. image:: https://raw.githubusercontent.com/yvesalexandre/bandicoot/master/docs/_static/bandicoot-dashboard.png
    :alt: Bandicoot interactive visualization

---------------
Where to get it
---------------

The source code is currently hosted on Github at https://github.com/yvesalexandre/bandicoot. Binary installers for the latest released version are available at the Python package index:

    http://pypi.python.org/pypi/bandicoot/

And via `easy_install`:

.. code-block:: sh

    easy_install bandicoot

or  `pip`:

.. code-block:: sh

    pip install bandicoot

------------
Dependencies
------------

bandicoot has no dependencies, which allows users to easily compute indicators on a production machine. To run tests and compile the visualization, optional dependencies are needed:

- `nose <http://nose.readthedocs.io/en/latest/>`_, `numpy <http://www.numpy.org/>`_, `scipy <https://www.scipy.org/>`_, and `networkx <https://networkx.github.io/>`_ for tests,
- `npm <http://npmjs.com>`_ to compile the js and css files of the dashboard.

-------
Licence
-------

MIT

-------------
Documentation
-------------

The official documentation is hosted on http://bandicoot.mit.edu/docs. It includes a quickstart tutorial, a detailed reference for all functions, and guides on how to use and extend bandicoot.
