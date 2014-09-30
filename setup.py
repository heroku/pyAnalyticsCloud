#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.md').read()

requirements = [
    'sqlalchemy',
    'psycopg2',
    'unicodecsv',
    'salesforce-python-toolkit',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pyAnalyticsCloud',
    version='0.1.0',
    description='Tools to help load data into Salesforce.com Analytics Cloud',
    long_description=readme,
    author='Marc Sibson',
    author_email='marc@heroku.com',
    url='https://github.com/heroku/pyAnalyticsCloud',
    packages=[ 'analyticscloud', 'analyticscloud.importers'],
    entry_points={
        'console_scripts': [
            'pyac-metadata=analyticscloud.commandline:metadata',
            'pyac-upload=analyticscloud.commandline:upload',
            'pyac-table=analyticscloud.commandline:table',
            'pyac-dump=analyticscloud.commandline:dump',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='salesforce, heroku, insights',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
