import salesforce_oauth_request


class SFSoapConnection(object):

    def __init__(sefl, url, access_token, refresh_token):
        pass


def login(username, password, client_id, client_secret, redirect_url):
    return 'x', 'y', 'z'
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
        metadata = self.importer.metadata_schema()
        print 'META', metadata
        records = list(self.importer)
