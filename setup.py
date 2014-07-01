"""
Setup script for libyate
"""

from setuptools import setup

import libyate


setup(
    name='libyate',
    url='https://bitbucket.org/asenci/libyate',
    license='ISC License',
    author='Andre Sencioles Vitorio Oliveira',
    author_email='andre@bcp.net.br',
    description='Python library for developing Yate external applications',
    long_description='A more "pythonic" approach to Yate.',
    version=libyate.__version__,
    packages=['libyate'],
    test_suite="tests",
    platforms='any',
    keywords=[
        'yate',
    ]
)
