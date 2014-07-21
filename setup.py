#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
    'click',
    'nltk',
    'scikit-learn',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='clicon',
    version='0.1dev',
    description='A tool for clinical concept extraction.',
    long_description=readme + '\n\n' + history,
    url='https://github.com/mitmedg/CliCon',
    packages=[
        'clicon',
    ],
    package_dir={'clicon':
                 'clicon'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='clicon',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points='''
        [console_scripts]
        clicon=clicon.cli:clicon
    ''',
)