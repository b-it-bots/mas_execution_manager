#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['mas_execution_manager'],
    package_dir={'mas_execution_manager': 'ros/src/mas_execution_manager'}
)

setup(**d)
