import json
import base64

from cpm.domain.plugin_download import PluginDownload
from cpm.infrastructure import http_client


class CpmHubConnectorV1(object):
    def __init__(self, filesystem, repository_url='https://www.cpm-hub.com/api/v1/plugins'):
        self.filesystem = filesystem
        self.repository_url = repository_url

    def publish_plugin(self, project, file_name):
        payload = base64.b64encode(self.filesystem.read_file(file_name, 'rb')).decode('utf-8')
        body = {
            'plugin_name': project.name,
            'version': project.version,
            'payload': payload
        }

        http_client.post(self.repository_url, data=json.dumps(body))

    def download_plugin(self, plugin_name):
        response = json.loads(http_client.get(f'{self.repository_url}/{plugin_name}'))
        return PluginDownload(response['plugin_name'], response['version'], response['payload'])


class AuthenticationFailure(RuntimeError):
    pass
