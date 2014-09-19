# -*- coding: utf-8 -*-

import optparse

from .insights import InsightsUploader
from importers.db import DBImporter

def table_iterator(dbengine, table):
    return []


def main():
    usage = '%prog table [table]'
    op = opparse.OptionParser(usage=usage)

    op.add_option('--url', default='postgresql://localhost',
                  help='Database URL to connect to')

    options, args = op.parse_args()
    if not args:
        op.error('need at least one table to upload')

    for table in args:
        importer = DBImporter(options.url, table)
        uploader = InsightsUploader(importer)


if __name__ == '__main__':
    main()
