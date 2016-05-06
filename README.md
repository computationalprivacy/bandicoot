<h1><span>bandicoot</span>
    <a href="https://pypi.python.org/pypi/bandicoot"><img src="https://img.shields.io/pypi/v/bandicoot.svg" alt="version"></a>
    <a href="https://github.com/yvesalexandre/bandicoot/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/bandicoot.svg" alt="licence"></a>
    <a href="https://pypi.python.org/pypi/bandicoot"><img src="https://img.shields.io/pypi/dm/bandicoot.svg" alt="downloads"></a>
    <a href="https://travis-ci.org/yvesalexandre/bandicoot"><img src="https://img.shields.io/travis/yvesalexandre/bandicoot.svg" alt="build"></a>
</h1>

**bandicoot** ([http://bandicoot.mit.edu](http://bandicoot.mit.edu)
) is Python toolbox to analyze mobile phone metadata. It provides a complete, easy-to-use environment for data-scientist to analyze mobile phone metadata. With only a few lines of code, load your datasets, visualize the data, perform analyses, and export the results. 


<p align="center">
  <img src="https://raw.githubusercontent.com/yvesalexandre/bandicoot/master/docs/_static/bandicoot-dashboard.png" width="600"/><br /><span>Bandicoot interactive visualization</span>
</p>


## Where to get it

The source code is currently hosted on Github at [https://github.com/yvesalexandre/bandicoot](https://github.com/yvesalexandre/bandicoot). Binary installers for the latest released version are available at the Python package index:

    http://pypi.python.org/pypi/bandicoot/

And via `easy_install`:

```sh
easy_install bandicoot
```

or  `pip`:

```sh
pip install bandicoot
```

## Dependencies

bandicoot has no dependencies, which allows users to easily compute indicators on a production machine. To run tests and compile the visualization, optional dependencies are needed:

- [numpy](http://www.numpy.org/), [scipy](https://www.scipy.org/), and [networkx](https://networkx.github.io/) for tests,
- [npm](http://npmjs.com) to compile the js and css files of the dashboard.

## Licence

MIT

## Documentation

The official documentation is hosted on [bandicoot.mit.edu/docs](http://bandicoot.mit.edu/docs). It includes a quickstart tutorial, a detailed reference for all functions, and guides on how to use and extend bandicoot.
