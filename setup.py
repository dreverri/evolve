from setuptools import setup, find_packages
import sys
import os

version = '0.1'

setup(name='Evolve',
    version=version,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    tests_require="nose",
    install_requires=["sqlalchemy", "sqlalchemy-migrate"],
    scripts=['bin/evolve']
    )