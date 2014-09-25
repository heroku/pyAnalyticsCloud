hc-insights
===========
Tooling to push data into SFDC Insights.
hc-insights can be used as a set of command line tools to prepare and upload data or as a library.


.. image:: https://badge.fury.io/py/hc-insights.png
    :target: http://badge.fury.io/py/hc-insights

.. image:: https://travis-ci.org/sibson/hc-insights.png?branch=master
        :target: https://travis-ci.org/sibson/hc-insights

.. image:: https://pypip.in/d/hc-insights/badge.png
        :target: https://pypi.python.org/pypi/hc-insights


The quickest way to get started is to deploy 
[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/heroku/hc-insights)

Usage
--------

hci-table postgres://localhost/dvdrental rental
 
hci-metadata postgres://localhost/dvdrental rental > metadata.json
hci-dump postgres://localhost/dvdrental rental > data.csv
hci-upload metadata.json data.csv
