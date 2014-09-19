from StringIO import StringIO

import unicodecsv


class SFSoapConnection(object):

    def __init__(sefl, url, access_token, refresh_token):
        pass

    def start(self, metadata):
        print 'NEW UPLOAD', metadata

    def upload(self, data):
        print 'UPLOADING Records', data.read()

    def complete(self):
        print 'COMPELTE UPLOAD'


def login(username, password, client_id, client_secret, redirect_url):
    return range(3)

    creds = salesforce_oauth_request.login(
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_url)

    return creds['instance_url'], creds['access_token'], creds['refresh_token']


class InsightsUploader(object):
    MAX_FILE_SIZE = 1 * 1024 * 1024
    MAX_FILE_SIZE = 1024

    def __init__(self, importer, instance_url, access_token, refresh_token):
        self.importer = importer
        self.connection = SFSoapConnection(instance_url, access_token, refresh_token)
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

        object_metadata = self.importer.metadata_schema()
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
