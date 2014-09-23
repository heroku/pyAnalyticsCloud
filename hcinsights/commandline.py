# -*- coding: utf-8 -*-

import json
import optparse
import os.path

from . import insights
from importers.db import DBImporter


def main():
    usage = '%prog configfile table'
    op = optparse.OptionParser(usage=usage)

    options, args = op.parse_args()


    password = os.environ.get('HCINSIGHTS_SFDC_PASSWORD')
    if not password:
        op.error('Please provide your password via environment variable: HCINSIGHTS_SFDC_PASSWORD')

    try:
        config = args.pop(0)
    except ValueError:
        op.error('missing configfile')

    config = json.load(open(os.path.expanduser(config)))

    try:
        table = args.pop(0)
    except ValueError:
        op.error('missing table')

    importer = DBImporter(config['db'], table)

    creds = config['salesforce']
    connection = insights.SFSoapConnection(creds['username'], password)

    uploader = insights.InsightsUploader(importer, connection)
    uploader.upload(table)


if __name__ == '__main__':
    main
