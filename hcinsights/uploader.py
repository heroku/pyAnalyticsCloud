import json
from StringIO import StringIO
from base64 import b64encode

import beatbox
import unicodecsv


class ConnectionError(Exception):
    pass


class InsightsUploader(object):
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, metadata, data):
        self.metadata = metadata
        self.data = data

        self.ns = beatbox._tPartnerNS
        self.client = beatbox.Client()
        self.client.serverUrl = '/'.join([self.client.serverUrl.rsplit('/', 1)[0], '32.0'])
        self.parts = None

    def login(self, username, password):
        self.client.login(username, password)

    def oauth(self, sessionId, serverUrl=None):
        if serverUrl is None:
            serverUrl = self.client.serverUrl
        self.client.useSession(sessionId, serverUrl)

    def upload(self, edgemart):
        output = StringIO()
        writer = unicodecsv.writer(output, encoding='utf-8')

        self.start(edgemart, json.dumps(self.metadata))

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


    def _get_error(self, response):
        return dict(
            status_code=str(response[self.ns.errors][self.ns.statusCode]),
            message=str(response[self.ns.errors][self.ns.message]),
            response=response)

    def _is_success(self, response):
        return str(response[self.ns.success]) == 'true'

    def start(self, edgemart, metadata):
        self.parts = []
        response = self.client.create([{
            'type': 'InsightsExternalData',
            'EdgemartAlias': edgemart,
            'EdgemartContainer': '',
            'MetadataJson': b64encode(metadata),
            'Format': 'CSV',
            'Operation': 'Overwrite',
            'Action': 'None'
        }])

        if not self._is_success(response):
            raise ConnectionError(
                'creating InsightsExternalData object: {}'.format(self._get_error(reponse)))

        self.data_id = str(response[self.ns.id])

    def add_data(self, data):
        response = self.client.create([{
            'type': 'InsightsExternalDataPart',
            'PartNumber': len(self.parts) + 1,
            'InsightsExternalDataId': self.data_id,
            'DataFile': b64encode(data.read())
        }])

        if not self._is_success(response):
            raise ConnectionError(
                'creating InsightsExternalDataPart object: {}'.format(self._get_error(response)))
        self.parts.append(str(response[self.ns.id]))

    def complete(self):
        response = self.client.update([{
            'type': 'InsightsExternalData',
            'Id': self.data_id,
            'Action': 'Process'
        }])

        if not self._is_success(response):
            raise ConnectionError(
                'updating InsightsExternalData object: {}'.format(self._get_error(response)))


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
