hc-insights
===========
[![Python](https://badge.fury.io/py/hc-insights.png)](http://badge.fury.io/py/hc-insights)
[![TravisCI](https://travis-ci.org/sibson/hc-insights.png?branch=master)](https://travis-ci.org/sibson/hc-insights)
[![PyPi](https://pypip.in/d/hc-insights/badge.png)](https://pypi.python.org/pypi/hc-insights)

Tooling to push data into SFDC Insights.
hc-insights can be used as a set of command line tools to prepare and upload data or as a library.


The quickest way to get started is to [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/heroku/hc-insights)

Usage
--------
You can also use If you want more flexibility you can use the command line tools.
First, you will need to set your SFDC credencials in environment variables.
The password is a combination of your login password and your SFDC token.

    export HCINSIGHTS_SFDC_USERNAME=youruser@example.com
    export HCINSIGHTS_SFDC_PASSWORD=yourpasswordYOURTOKEN

If you want to quickly load a table into Insights you can run, which is similar to what the Web UI does

    hci-table postgres://username:password@db.example.com/database table_name

Loading data into Insights is basically a three step process.

  1. generate a CSV file with your data
  2. generate a JSON file containing metadata describing your data
  3. upload the metadata and data to insights

hc-insights provides a command to help with each stage.

    hci-dump postgres://username:password@db.example.com/database table_name > data.csv
    hci-metadata postgres://username:password@db.example.com/database table_name > metadata.json
    hci-upload metadata.json data.csv

This can be useful if you want to futher customize the generated metadata to rename field or provide richer description
s

Library
---------
If you need to further customize how the data is prepared prior to upload you can use hc-insights as a library when writing your own import scripts.
