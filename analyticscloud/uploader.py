import csv
import numbers
import json
import logging
import os.path
from datetime import datetime

from base64 import b64encode
from StringIO import StringIO

from sforce.partner import SforcePartnerClient
import unicodecsv


log = logging.getLogger('analyticscloud.uploader')


def _stringify(s, encoding, errors):
    # customize the date
    if isinstance(s, datetime):
        return s.strftime('%Y-%m-%d %H:%M:%S')

    if s is None:
        return ''

    if isinstance(s, unicode):
        return s.encode(encoding, errors)

    if isinstance(s, numbers.Number):
        return s  # let csv.QUOTE_NONNUMERIC do its thing.

    if not isinstance(s, str):
        s = str(s)

    return s


def _stringify_list(l, encoding, errors='strict'):
    try:
        return [_stringify(s, encoding, errors) for s in iter(l)]
    except TypeError as e:
        raise csv.Error(str(e))


class AnalyticsWriter(unicodecsv.writer):
    def writerow(self, row):
        # override writerow so we can properly serialize dates
        return self.writer.writerow(_stringify_list(row, self.encoding, self.encoding_errors))


class ConnectionError(Exception):
    pass


class AnalyticsCloudUploader(object):
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, metadata, data, client=None):
        # XXX serve via public github? ok to publish?
        self.metadata = metadata
        self.data = data

        self.client = client
        self.parts = None

    def login(self, wsdl, username, password, token):
        self.client = SforcePartnerClient(wsdl)
        self.client.login(username, password, token)

    def upload(self, edgemart):
        output = StringIO()
        writer = AnalyticsWriter(output, encoding='utf-8')

        self.start(edgemart, self.metadata)

        biggest_record = 0
        for record in self.data:
            before_write = output.tell()
            writer.writerow(record)
            after_write = output.tell()
            record_size = after_write - before_write
            biggest_record = max(biggest_record, record_size * 2)

            if after_write + biggest_record > self.MAX_FILE_SIZE:
                output.seek(0)
                self.add_data(output)
                output.truncate(0)

        if output.tell():
            output.seek(0)
            self.add_data(output)

        self.complete()

    def start(self, edgemart, metadata):
        log.info('starting upload %s', edgemart)
        self.parts = []
        obj = self.client.generateObject('InsightsExternalData')
        obj.EdgemartAlias = edgemart
        obj.EdgemartContainer = ''
        obj.MetadataJson = b64encode(json.dumps(metadata))
        obj.Format = 'CSV'
        obj.Operation = 'Overwrite'
        obj.Action = None

        result = self.client.create(obj)
        if not result.success:
            raise ConnectionError(result)
        self.data_id = result.id

    def add_data(self, data):
        log.info('uploading chunk')
        obj = self.client.generateObject('InsightsExternalDataPart')
        obj.PartNumber = len(self.parts) + 1
        obj.InsightsExternalDataId = self.data_id
        obj.DataFile = b64encode(data.read())
        result = self.client.create(obj)
        if not result.success:
            raise ConnectionError(result)
        self.parts.append(result)

    def complete(self):
        log.info('upload complete')
        obj = self.client.generateObject('InsightsExternalData')
        obj.Id = self.data_id
        obj.Action = 'Process'
        result = self.client.update(obj)
        if not result.success:
            raise ConnectionError(result)


class DataFileChunker(AnalyticsCloudUploader):
    metadata = None

    def __init__(self, datafile, encode=True):
        self.datafile = datafile
        self.encode = encode
        self.output_format = os.path.splitext(os.path.basename(datafile))[0] + '-{:0>3d}.csv'
        self.parts = []

    def start(self, edgemart, metadata):
        self.data = unicodecsv.reader(open(self.datafile))

    def add_data(self, data):
        with (open(self.output_format.format(len(self.parts) + 1), 'w')) as output:
            if self.encode:
                data = b64encode(data.read())
            else:
                data = data.read()
            result = output.write(data)
        self.parts.append(result)

    def complete(self):
        return
