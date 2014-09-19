import beatbox
import json
import salesforce_oauth_request


class SFSoapConnection(object):
    def __init__(self, username, password):
        self.ns = beatbox._tPartnerNS
        self.client = beatbox.Client()
        self.client.serverUrl = '/'.join([svc.serverUrl.rsplit('/', 1)[0], '32.0'])
        self.client.login(username, password)

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
    def __init__(self, importer, username, password):
        self.importer = importer
        self.connection = SFSoapConnection(username, password)

    def upload(self, edge_alias, edge_container):
        metadata = self.importer.get_metadata()
        # create InsightsExternalData object
        data_id, error = self.connection.create({
            'type': 'InsightsExternalData',
            'EdgemartAlias': edge_alias,
            'EdgemartContainer': edge_container,
            # not sure what this format needs to be..
            # from Java sample looks like we can use a string
            'MetadataJson': json.dumps(metada),
            'Format': 'CSV',
            'Operation': 'Overwrite',
            'Action': 'None'
        })

        if error is not None:
            # How are we handling errors? Raise an exception?
            pass

        # upload parts
        part_index = 0
        parts_ids = []
        for chunk in self.importer:
            part_index += 1
            partd_id, error = self.connection.create({
                'type': 'InsightsExternalDataPart',
                'PartNumber': part_index,
                'InsightsExternalDataId': data_id,
                # assuming these are like StringIO() objects?
                'DataFile': chunk.read()
            })

            chunk.close()

            if error is not None:
                pass

        # update Action
        update_data_id, error = self.connection.update({
            'type': 'InsightsExternalData',
            'Id': data_id,
            'Action': 'Process'
        })

        if error is not None:
            pass
