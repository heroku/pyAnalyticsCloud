import json
from StringIO import StringIO
from base64 import b64encode

from sforce.partner import SforcePartnerClient
import unicodecsv


class ConnectionError(Exception):
    pass


class InsightsUploader(object):
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
        writer = unicodecsv.writer(output, encoding='utf-8')

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
            raise ConnectionError('failed to start upload')
        self.data_id = result.id

    def add_data(self, data):
        obj = self.client.generateObject('InsightsExternalDataPart')
        obj.PartNumber = len(self.parts) + 1
        obj.InsightsExternalDataId = self.data_id
        obj.DataFile = b64encode(data.read())
        result = self.client.create(obj)
        if not result.success:
            raise ConnectionError('failed to upload part')
        self.parts.append(result)

    def complete(self):
        obj = self.client.generateObject('InsightsExternalData')
        obj.Id = self.data_id
        obj.Action = 'Process'
        result = self.client.update(obj)
        if not result.success:
            raise ConnectionError('failed to mark upload complete')


def main():
    import optparse
    import os.path

    usage = '%prog edgemart metadata.json data.csv'

    op = optparse.OptionParser(usage=usage)

    options, args = op.parse_args()

    try:
        edgemart = args.pop(0)
        metadata = args.pop(0)
        data = args.pop(0)
    except IndexError:
        op.error('missing args')

    username = os.environ.get('HCINSIGHTS_SFDC_USERNAME')
    if not username:
        op.error('Provide your password via environment variable: HCINSIGHTS_SFDC_USERNAME')

    password = os.environ.get('HCINSIGHTS_SFDC_PASSWORD')
    if not password:
        op.error('Provide your password via environment variable: HCINSIGHTS_SFDC_PASSWORD')

    connection = SFSoapConnection(username, password, edgemart, None)
    connection.start(open(metadata).read())
    connection.upload(open(data))
    connection.complete()


if __name__ == '__main__':
    main()
