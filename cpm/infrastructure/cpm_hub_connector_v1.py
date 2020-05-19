import json
import base64
from getpass import getpass
from http import HTTPStatus

from cpm.domain.install_service import BitNotFound
from cpm.domain.bit_download import BitDownload
from cpm.infrastructure import http_client


class CpmHubConnectorV1(object):
    def __init__(self, filesystem, repository_url='https://repo.cpmbits.com:8000'):
        self.filesystem = filesystem
        self.repository_url = repository_url

    def publish_bit(self, project, file_name):
        payload = base64.b64encode(self.filesystem.read_file(file_name, 'rb')).decode('utf-8')
        username = input('username: ')
        password = getpass(prompt='password: ', stream=None)
        body = {
            'bit_name': project.name,
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

    def download_bit(self, name, version):
        response = http_client.get(self.__bit_url(name, version))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise BitNotFound(f'{name}:{version}')

        data = json.loads(response.body)
        return BitDownload(data['bit_name'], data['version'], data['payload'])

    def __bit_url(self, name, version):
        return f'{self.repository_url}/{name}' if version == "latest" else f'{self.repository_url}/{name}/{version}'


class AuthenticationFailure(RuntimeError):
    pass


class InvalidCpmHubUrl(RuntimeError):
    pass


class PublicationFailure(RuntimeError):
    pass
