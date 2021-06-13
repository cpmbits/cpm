import json
import base64
from getpass import getpass
from http import HTTPStatus

from cpm.domain.template_download import TemplateDownload
from cpm.infrastructure import http_client
from cpm.infrastructure import filesystem
from cpm.domain.bit_download import BitDownload


class CpmHubConnectorV1(object):
    def __init__(self, repository_url='https://repo.cpmbits.com:8000', dry_run=False):
        self.dry_run = dry_run
        self.repository_url = repository_url

    def publish_bit(self, project_descriptor, file_name):
        payload = base64.b64encode(filesystem.read_file(file_name, 'rb')).decode('utf-8')
        username = input('username: ')
        password = getpass(prompt='password: ', stream=None)
        body = {
            'bit_name': project_descriptor.name,
            'version': project_descriptor.version,
            'payload': payload,
            'username': username,
            'password': password,
        }

        if self.dry_run:
            print(f'cpm: publishing to {self.repository_url}')
            print(json.dumps(body))
            return

        response = http_client.post(f'{self.repository_url}/bits', data=json.dumps(body))
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise AuthenticationFailure()
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise InvalidCpmHubUrl()
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise PublicationFailure("bad request")
        if response.status_code == HTTPStatus.CONFLICT:
            raise PublicationFailure(
                f'bit {project_descriptor.name}:{project_descriptor.version} has already been used and cannot be published again')
        if response.status_code != HTTPStatus.OK:
            raise PublicationFailure("cpm-hub returned error")

    def publish_template(self, project_descriptor, file_name):
        payload = base64.b64encode(filesystem.read_file(file_name, 'rb')).decode('utf-8')
        username = input('username: ')
        password = getpass(prompt='password: ', stream=None)
        body = {
            'template_name': project_descriptor.name,
            'version': project_descriptor.version,
            'payload': payload,
            'username': username,
            'password': password,
        }

        if self.dry_run:
            print(f'cpm: publishing to {self.repository_url}')
            print(json.dumps(body))
            return

        response = http_client.post(f'{self.repository_url}/templates', data=json.dumps(body))
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise AuthenticationFailure()
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise InvalidCpmHubUrl()
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise PublicationFailure("bad request")
        if response.status_code == HTTPStatus.CONFLICT:
            raise PublicationFailure(
                f'bit {project_descriptor.name}:{project_descriptor.version} has already been used and cannot be published again')
        if response.status_code != HTTPStatus.OK:
            raise PublicationFailure("cpm-hub returned error")

    def download_bit(self, name, version):
        response = http_client.get(self.__bit_url(name, version))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise BitNotFound(f'{name}:{version}')

        data = json.loads(response.body)
        return BitDownload(data['bit_name'], data['version'], data['payload'])

    def __bit_url(self, name, version):
        if version == "latest":
            return f'{self.repository_url}/bits/{name}'
        else:
            return f'{self.repository_url}/bits/{name}/{version}'

    def download_template(self, name, version):
        response = http_client.get(self.__template_url(name, version))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise TemplateNotFound(f'{name}:{version}')

        data = json.loads(response.body)
        return TemplateDownload(data['template_name'], data['version'], data['payload'])

    def __template_url(self, name, version):
        if version == "latest":
            return f'{self.repository_url}/templates/{name}'
        else:
            return f'{self.repository_url}/templates/{name}/{version}'


class AuthenticationFailure(RuntimeError):
    pass


class InvalidCpmHubUrl(RuntimeError):
    pass


class PublicationFailure(RuntimeError):
    pass


class BitNotFound(RuntimeError):
    pass


class TemplateNotFound(RuntimeError):
    pass
