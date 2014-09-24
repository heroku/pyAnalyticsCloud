# -*- coding: utf-8 -*-

import json
import optparse
import os.path
import sys

import unicodecsv

from . import insights
from importers import db


def get_credencials(optionparser):
    username = os.environ.get('HCINSIGHTS_SFDC_USERNAME')
    if not username:
        optionparser.error('HCINSIGHTS_SFDC_USERNAME, missing from environment')

    password = os.environ.get('HCINSIGHTS_SFDC_PASSWORD')
    if not password:
        optionparser.error('HCINSIGHTS_SFDC_PASSWORD, missing from environment')

    return username, password


def get_arg(option_parser, args, error_message='', default=None):
    try:
        return args.pop(0)
    except IndexError:
        if default:
            return default

        option_parser.error(error_message)


def metadata():
    usage = '%prog dburl table [edgemart]'
    op = optparse.OptionParser(usage=usage)

    opts, args = op.parse_args()
    username, password = get_credencials(op)

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    table = get_arg(op, args, 'missing table')

    metadata = db.generate_metadata(dburl, table)

    print json.dumps(metadata, sort_keys=True, indent=4)


def dump():
    usage = '%prog dburl table'

    op = optparse.OptionParser(usage=usage)
    op.add_option('-o', '--output', metavar='FILENAME',
                  help='output data to FILENAME')

    options, args = op.parse_args()

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    table = get_arg(op, args, 'missing table')

    if options.output:
        output = open(options.output, 'w')
    else:
        output = sys.stdout

    writer = unicodecsv.writer(output, encoding='utf-8')
    for record in db.data_generator(dburl, table):
        writer.writerow(record)


def upload():
    usage = '%prog metadata.json data.csv [edgemart]'
    op = optparse.OptionParser(usage=usage)

    options, args = op.parse_args()
    username, password = get_credencials(op)

    metadata = get_arg(op, args, 'missing metadata.json')
    metadata = json.loads(open(metadata).read())

    datafile = get_arg(op, args, 'missing datafile.csv')

    edgemart = get_arg(op, args, default=json.loads(metadata)['objects'][0]['name'])

    connection = insights.SFSoapConnection(username, password)
    data = open(datafile).xreadlines()

    uploader = insights.InsightsUploader(connection, metadata, data)
    uploader.upload(edgemart)


def table():
    usage = '%prog dburl table [edgemart]'
    op = optparse.OptionParser(usage=usage)

    options, args = op.parse_args()
    username, password = get_credencials(op)

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    table = get_arg(op, args, 'missing table')
    edgemart = get_arg(op, args, default=table)

    connection = insights.SFSoapConnection(username, password)
    metadata = db.generate_metadata(dburl, table)
    data = db.data_generator(dburl, table)

    uploader = insights.InsightsUploader(connection, metadata, data)
    uploader.upload(edgemart)


if __name__ == '__main__':
    table()
