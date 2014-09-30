# -*- coding: utf-8 -*-

import codecs
import json
import optparse
import os.path
import sys

import unicodecsv

from analyticscloud.uploader import AnalyticsCloudUploader
from importers import db


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


def metadata():
    usage = '%prog dburl table [edgemart]'
    op = optparse.OptionParser(usage=usage)
    op.add_option('-o', '--output', metavar='FILENAME',
                  help='output data to FILENAME', default=sys.stdout)

    opts, args = op.parse_args()

    if opts.output != sys.stdout:
        opts.output = open(opts.output, 'w')

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    table = get_arg(op, args, 'missing table')

    metadata = db.metadata_dict(dburl, table)

    json.dump(metadata, opts.output, sort_keys=True, indent=4)


def dump():
    usage = '%prog dburl table'

    op = optparse.OptionParser(usage=usage)
    op.add_option('-o', '--output', metavar='FILENAME',
                  help='output data to FILENAME', default=sys.stdout)

    options, args = op.parse_args()

    dburl = get_arg(op, args, 'missing dburl, [postgres://username:password@localhost/database]')
    table = get_arg(op, args, 'missing table')

    if options.output != sys.stdout:
        options.output = open(options.output, 'w', newline='')

    writer = unicodecsv.writer(options.output, encoding='utf-8')
    for record in db.data_generator(dburl, table):
        writer.writerow(record)


def upload():
    usage = '%prog metadata.json data.csv [edgemart]'
    op = optparse.OptionParser(usage=usage)
    op.add_option('--wsdl', default='wsdl_partner.xml')
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
    table = get_arg(op, args, 'missing table')
    edgemart = get_arg(op, args, default=table)

    metadata = db.metadata_dict(dburl, table)
    data = db.data_generator(dburl, table)

    uploader = AnalyticsCloudUploader(metadata, data)
    uploader.login(options.wsdl, username, password, token)
    uploader.upload(edgemart)


if __name__ == '__main__':
    table()
