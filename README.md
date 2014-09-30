[![Python](https://badge.fury.io/py/hc-insights.png)](http://badge.fury.io/py/hc-insights)
[![TravisCI](https://travis-ci.org/sibson/hc-insights.png?branch=master)](https://travis-ci.org/sibson/hc-insights)
[![PyPi](https://pypip.in/d/hc-insights/badge.png)](https://pypi.python.org/pypi/hc-insights)

Heroku Connect Insights Loader
====================================
Tooling to push data into SFDC Analytics Cloud.
hc-insights can be either be used as a set of command line tools or as a library.

Usage
--------
First, you will need to set your SFDC credencials via environment variables.

    export SFDC_USERNAME=youruser@example.com
    export SFDC_PASSWORD=yourpassword
    export SFDC_TOKEN=yourtoken

More information about getting your [Security Token](https://help.salesforce.com/apex/HTViewHelpDoc?id=user_security_token.htm)

The quickest way to get started is to load an entire table into SFDC Analytics, Insights

    pyac-table postgres://username:password@db.example.com/database table_name

This command will execute the following three step process.

  1. generate a JSON file containing metadata describing your data
  2. generate a CSV file with your data
  3. upload the metadata and data to Analytics Cloud

pyAnalyticsCloud also provides commands help with each step, this allows you to customize your data before upload

    pyac-metadata postgres://username:password@db.example.com/database table_name -o metadata.json
    pyac-dump postgres://username:password@db.example.com/database table_name -o data.csv
    pyac-upload metadata.json data.csv

Rather than manually editing the datafiles, you may want to simply create a new DB table that is populated with your data and use pyac-table.

Library
---------
If you want to develop more advanced workflows you can use pyAnalyticsCloud as a library for a Python application.
