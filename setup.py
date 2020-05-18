#!/usr/bin/env python

from setuptools import setup

long_description = open('README.rst').read()


setup(
    name='bandicoot',
    author='Yves-Alexandre de Montjoye',
    author_email='yvesalexandre@demontjoye.com',
    version="0.6.0",
    url="https://github.com/computationalprivacy/bandicoot",
    license="MIT",
    packages=[
        'bandicoot',
        'bandicoot.helper',
        'bandicoot.tests'
    ],
    include_package_data=True,
    description="A toolbox to analyze mobile phone metadata.",
    long_description=long_description,
    classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics'
    ],
    extras_require={
        'tests': ['numpy', 'scipy', 'networkx']
    })
