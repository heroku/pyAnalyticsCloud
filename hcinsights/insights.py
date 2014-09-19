import salesforce_oauth_request


class SFSoapConnection():
    pass


def login(username, password, client_id, client_secret, redirect_url):
    creds = salesforce_oauth_request.login(
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_url)

    return creds['instance_url'], creds['access_token'], creds['refresh_token']


class InsightsUploader(object):
    def __init__(self, importer, instance_url, access_token, refresh_token):
        self.importer = importer
        self.connection = SFSoapConnection(instance_url, access_token, refresh_token)

    def upload(self):
        metadata = importer.metadata_schema()
        for chunk in self._chunk_data():
            self.connection.upload_file(chunk)

    def _chunk_data(self):
        pass
