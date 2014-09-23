# -*- coding: utf-8 -*-

import json
import optparse
import os.path

from . import insights
from importers.db import DBImporter


def main():
    usage = '%prog configfile'
    op = optparse.OptionParser(usage=usage)

    options, args = op.parse_args()

    if not args:
        op.error('Please provide a run config file')

    password = os.environ.get('HCINSIGHTS_SFDC_PASSWORD')
    if not password:
        op.error('Please provide your password via environment variable: HCINSIGHTS_SFDC_PASSWORD')

    config = json.load(open(os.path.expanduser(args[0])))

    importer = DBImporter(config['db'])

    creds = config['salesforce']
    connection = insights.SFSoapConnection(creds['username'], password, creds['edgemart_alias'])

    uploader = insights.InsightsUploader(importer, connection)
    uploader.upload()


if __name__ == '__main__':
    main
