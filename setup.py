#!/usr/bin/env python3

from setuptools import setup

requirements = [
    'notmuch',
]


setup(
    name='prosa',
    description='A standards based terminal calendar',
    packages=['prosa'],
    install_requires=requirements,
)
