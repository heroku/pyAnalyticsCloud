# -*- coding: utf-8 -*-

import codecs
import json
import optparse
import os.path
import sys

import unicodecsv

from analyticscloud.uploader import AnalyticsCloudUploader, DataFileChunker, AnalyticsWriter
from importers import db


WSDL = os.path.join(os.path.dirname(__file__), 'wsdl_partner.xml')


def get_credentials(optionparser):
    username = os.environ.get('SFDC_USERNAME')
    if not username:
        optionparser.error('SFDC_USERNAME, missing from environment')

    password = os.environ.get('SFDC_PASSWORD')
    if not password:
        optionparser.error('SFDC_PASSWORD, missing from environment')

    token = os.environ.get('SFDC_TOKEN')
    if not token:
        optionparser.error('SFDC_TOKEN, missing from environment')

    return username, password, token


def get_arg(option_parser, args, error_message='', default=None):
    try:
        return args.pop(0)
    except IndexError:
        if default:
            return default

        option_parser.error(error_message)


def get_schema_table(option_parser, args):
    table = get_arg(option_parser, args, 'missing table')
    try:
        schema, table = table.split('.')
    except ValueError:
        schema = 'public'

    return schema, table


def metadata():
    usage = '%prog dburl table [edgemart]'
    op = optparse.OptionParser(usage=usage)
    op.add_option('-o', '--output', metavar='FILENAME',
                  help='output data to FILENAME', default=sys.stdout)

    opts, args = op.parse_args()

    if opts.output != sys.stdout:
        opts.output = open(opts.output, 'w')

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    schema, table = get_schema_table(op, args)
    metadata = db.metadata_dict(dburl, table, schema=schema)

    json.dump(metadata, opts.output, sort_keys=True, indent=4)


def dump():
    usage = '%prog dburl table'

    op = optparse.OptionParser(usage=usage)
    op.add_option('-o', '--output', metavar='FILENAME',
                  help='output data to FILENAME', default=sys.stdout)
    op.add_option('-l', '--limit', metavar='COUNT', type='int',
                  help='limit dump to COUNT records')

    options, args = op.parse_args()

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    schema, table = get_schema_table(op, args)

    if options.output != sys.stdout:
        options.output = open(options.output, 'w', newline='')

    writer = AnalyticsWriter(options.output, encoding='utf-8')
    for record in db.data_generator(dburl, table, schema=schema):
        writer.writerow(record)
        if options.limit is not None:
            options.limit -= 1
            if options.limit <= 0:
                break


def upload():
    usage = '%prog metadata.json data.csv [edgemart]'
    op = optparse.OptionParser(usage=usage)
    op.add_option('--wsdl', default=WSDL)
    options, args = op.parse_args()
    username, password, token = get_credentials(op)

    metadata = get_arg(op, args, 'missing metadata.json')
    metadata = json.loads(open(metadata, 'r').read())

    datafile = get_arg(op, args, 'missing datafile.csv')
    data = unicodecsv.reader(open(datafile))

    edgemart = get_arg(op, args, default=metadata['objects'][0]['name'])

    uploader = AnalyticsCloudUploader(metadata, data)
    uploader.login(options.wsdl, username, password, token)
    uploader.upload(edgemart)


def table():
    usage = '%prog dburl table [edgemart]'
    op = optparse.OptionParser(usage=usage)
    op.add_option('--wsdl', default='wsdl_partner.xml')
    options, args = op.parse_args()
    username, password, token = get_credentials(op)

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    schema, table = get_schema_table(op, args)
    edgemart = get_arg(op, args, default=table)

    metadata = db.metadata_dict(dburl, table, schema=schema)
    data = db.data_generator(dburl, table, schema=schema)

    uploader = AnalyticsCloudUploader(metadata, data)
    uploader.login(options.wsdl, username, password, token)
    uploader.upload(edgemart)


def chunk():
    usage = '%prog data.csv'
    op = optparse.OptionParser(usage=usage)
    op.add_option('-o', '--output', metavar='FILENAME',
                  help='output data to FILENAME', default=sys.stdout)
    op.add_option('-r', '--readable', action='store_true')

    options, args = op.parse_args()

    datafile = get_arg(op, args, 'missing csv file')
    chunker = DataFileChunker(datafile, encode=not options.readable)
    chunker.upload(os.path.basename(datafile))


if __name__ == '__main__':
    table()
