#!/usr/bin/env python
#
# Copyright 2016, Steve Milner
# Distributed under the Modified BSD License.
# See LICENSE for the full license text.
"""
Setup script.
"""

from setuptools import setup, find_packages


def extract_requirements(filename):
    """
    Extract requirements from a requirements file.
    """
    with open(filename, 'r') as requirements_file:
        return [x[:-1] for x in requirements_file.readlines()]


setup(
    name='petty',
    version='0.0.0',
    description=('Developer friendly gRPC based server with '
                 'additional functionality'),
    author='Steve Milner',
    maintainer='Steve Milner',
    url='https://github.com/ashcrow/petty',
    license="BSD",

    install_requires=extract_requirements('requirements.txt'),
    tests_require=extract_requirements('test-requirements.txt'),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ]
)
