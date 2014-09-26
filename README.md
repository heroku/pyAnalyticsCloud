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
The password is a combination of your login password and your SFDC token.

    export HCINSIGHTS_SFDC_USERNAME=youruser@example.com
    export HCINSIGHTS_SFDC_PASSWORD=yourpasswordYOURTOKEN

The quickets way to get started is to load an entire table into SFDC Analytics, Insights

    hci-table postgres://username:password@db.example.com/database table_name

Loading data into Insights is basically a three step process.

  1. generate a CSV file with your data
  2. generate a JSON file containing metadata describing your data
  3. upload the metadata and data to insights

hc-insights provides a CLI to help with each stage

    hci-dump postgres://username:password@db.example.com/database table_name > data.csv
    hci-metadata postgres://username:password@db.example.com/database table_name > metadata.json
    hci-upload metadata.json data.csv

This can be useful if you want to futher customize the generated metadata to rename field or provide richer descriptions

Library
---------
If you need to further customize how the data is prepared prior to upload you can use hc-insights as a library.
