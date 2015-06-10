#!/usr/bin/env python

from setuptools import setup
import re
import ast


_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('bandicoot/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='bandicoot',
    author='Yves-Alexandre de Montjoye',
    author_email='yvesalexandre@demontjoye.com',
    version=version,
    url="https://github.com/yvesalexandre/bandicoot",
    license="MIT",
    packages=[
        'bandicoot',
        'bandicoot.helper',
        'bandicoot.tests',
        'bandicoot.special'
    ],
    description="A toolbox to analyze mobile phone metadata.",
    classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics'
    ])
