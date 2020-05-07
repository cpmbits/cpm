import json
import base64
from getpass import getpass
from http import HTTPStatus

from cpm.domain.install_service import PluginNotFound
from cpm.domain.plugin_download import PluginDownload
from cpm.infrastructure import http_client
from cpm.infrastructure.http_client import HttpConnectionError


class CpmHubConnectorV1(object):
    def __init__(self, filesystem, repository_url='https://www.cpm-hub.com/api/v1/plugins'):
        self.filesystem = filesystem
        self.repository_url = repository_url

    def publish_plugin(self, project, file_name):
        payload = base64.b64encode(self.filesystem.read_file(file_name, 'rb')).decode('utf-8')
        username = input('username: ')
        password = getpass(prompt='password: ', stream=None)
        body = {
            'plugin_name': project.name,
            'version': project.version,
            'payload': payload,
            'username': username,
            'password': password,
        }

        response = http_client.post(self.repository_url, data=json.dumps(body))
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise AuthenticationFailure()
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise InvalidCpmHubUrl()
        if response.status_code != HTTPStatus.OK:
            raise PublicationFailure()

    def download_plugin(self, plugin_name):
        response = http_client.get(f'{self.repository_url}/{plugin_name}')
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise PluginNotFound

        data = json.loads(response.body)
        return PluginDownload(data['plugin_name'], data['version'], data['payload'])


class AuthenticationFailure(RuntimeError):
    pass


class InvalidCpmHubUrl(RuntimeError):
    pass


class PublicationFailure(RuntimeError):
    pass
