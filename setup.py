#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.md').read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='hcinsights',
    version='0.1.0',
    description='Load data into Salesforce.com Insights',
    long_description=readme,
    author='Marc Sibson',
    author_email='marc@heroku.com',
    url='https://github.com/heroku/hc-insights',
    packages=[
        'hcinsights',
    ],
    package_dir={'hcinsights':
                 'hcinsights'},
    entry_points={
        'console_scripts': [
            'hc-insights = hcinsights.commandline:main',
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
