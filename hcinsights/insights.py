import json
from StringIO import StringIO

import beatbox
import unicodecsv


class ConnectionError(Exception):
    pass


class SFSoapConnection(object):
    def __init__(self, username, password, edge_alias, edge_container):
        self.ns = beatbox._tPartnerNS
        self.client = beatbox.Client()
        self.client.serverUrl = '/'.join([self.client.serverUrl.rsplit('/', 1)[0], '32.0'])
        self.client.login(username, password)
        self.edge_alias = edge_alias
        self.edge_container = edge_container
        self.parts = []

    def _get_error(self, request):
        return dict(
            status_code=str(request[self.ns.errors][self.ns.statusCode]),
            message=str(request[self.ns.errors][self.ns.message]),
            request=request)

    def _is_success(self, request):
        return str(request[self.ns.success]) == 'true'

    def create(self, obj):
        assert 'type' in obj, 'Must specify object type.'
        request = self.client.create([obj])
        if self._is_success(request):
            return str(request[self.ns.id]), None
        return None, self._get_error(request)

    def update(self, obj):
        assert 'Id' in obj, 'Must specify object Id.'
        request = self.client.update(obj)
        if self._is_success(request):
            return str(request[self.ns.id]), None
        return None, self._get_error(request)

    def delete(self, obj_id):
        request = self.client.delete(obj_id)
        if self._is_success(request):
            return str(request[self.ns.id]), None
        return None, self._get_error(request)

    def start(self, metadata):
        self.data_id, error = self.create({
            'type': 'InsightsExternalData',
            'EdgemartAlias': self.edge_alias,
            'EdgemartContainer': self.edge_container,
            'MetadataJson': json.dumps(metadata),
            'Format': 'CSV',
            'Operation': 'Overwrite',
            'Action': 'None'
        })
        if error:
            raise ConnectionError('Error creating InsightsExternalData object: {}'.format(json.dumps(error)))

    def upload(self, data):
        part_id, error = self.create({
            'type': 'InsightsExternalDataPart',
            'PartNumber': len(self.parts) + 1,
            'InsightsExternalDataId': self.data_id,
            'DataFile': data.read()
        })
        if error:
            raise ConnectionError('Error creating InsightsExternalDataPart object: {}'.format(json.dumps(error)))
        self.parts.append(part_id)

    def complete(self):
        update_data_id, error = self.update({
            'type': 'InsightsExternalData',
            'Id': self.data_id,
            'Action': 'Process'
        })
        if error:
            raise ConnectionError('Error updating InsightsExternalData object: {}'.format(json.dumps(error)))


class InsightsUploader(object):
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, importer, connection):
        self.importer = importer
        self.connection = connection
        self.metadata = self._metadata()

    def _metadata(self):
        metadata = {
            'fileFormat': {
                "charsetName": "UTF-8",
                "fieldsEnclosedBy": "\"",
                "fieldsDelimitedBy": ",",
                "linesTerminatedBy": "\n",
                "numberOfLinesToIgnore": 1,
            },
            'objects': []
        }

        object_metadata = self.importer.object_metadata()
        object_metadata['connector'] = 'HerokuConnectInsights'
        metadata['objects'].append(object_metadata)

        return metadata

    def upload(self):
        output = StringIO()
        writer = unicodecsv.writer(output, encoding='utf-8')

        self.connection.start(self.metadata)
        fields = [f['label'] for f in self.metadata['objects'][0]['fields']]
        writer.writerow(fields)

        biggest_record = 0
        for record in self.importer:
            before_write = output.tell()
            writer.writerow(record)
            after_write = output.tell()
            record_size = after_write - before_write
            biggest_record = max(biggest_record, record_size * 2)

            if after_write + biggest_record > self.MAX_FILE_SIZE:
                output.seek(0)
                self.connection.upload(output)
                output.truncate(0)

        if output.tell():
            output.seek(0)
            self.connection.upload(output)

        self.connection.complete()
