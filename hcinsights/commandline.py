# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
import optparse
import os.path

from . import insights
from importers.db import DBImporter


def main():
    usage = '%prog table [table]'
    op = optparse.OptionParser(usage=usage)

    op.add_option('-c', '--configfile', default='~/.hcinsights.ini')

    options, args = op.parse_args()
    if not args:
        op.error('need at least one table to upload')

    config = ConfigParser()
    config.read([os.path.expanduser(options.configfile)])

    sfcreds = dict(config.items('salesforce'))
    password = os.environ['HCINSIGHTS_PASSWORD']
    auth_creds = insights.login(sfcreds['username'], password,
                                sfcreds['client_id'], sfcreds['client_secret'],
                                sfcreds['redirect_url'])

    for table in args:
        importer = DBImporter(dict(config.items('db')), table)
        connection = insights.SFSoapConnection(sfcreds['username'], password,
            sfcreds['edgemart_alias'], sfcreds['edgemart_container'])
        uploader = insights.InsightsUploader(importer, connection)
        uploader.upload()


if __name__ == '__main__':
    main()
