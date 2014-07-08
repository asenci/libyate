"""
Setup script for libyate
"""

from setuptools import setup

import libyate


setup(
    name=libyate.__title__,
    description=libyate.__summary__,
    long_description=open("README.rst").read(),
    url=libyate.__url__,

    author=libyate.__author__,
    author_email=libyate.__email__,
    license=libyate.__license__,

    version=libyate.__version__,

    packages=['libyate'],
    test_suite="tests",
    platforms='any',
    keywords=[
        'yate',
    ]
)
