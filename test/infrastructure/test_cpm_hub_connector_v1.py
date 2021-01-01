import unittest
from mock import patch
from mock import MagicMock

from http import HTTPStatus

from cpm.domain.install_service import BitNotFound
from cpm.domain.bit_download import BitDownload
from cpm.domain.project import Project
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure, InvalidCpmHubUrl, PublicationFailure
from cpm.infrastructure.http_client import HttpResponse


class TestCpmHubConnectorV1(unittest.TestCase):
    @patch('cpm.infrastructure.cpm_hub_connector_v1.filesystem')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_bit_posts_bit_with_base64_encoded_payload_and_user_credentials(self, getpass, input, http_client, filesystem):
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1()
        http_client.post.return_value = HttpResponse(200, '')
        filesystem.read_file.return_value = b'bit payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        connector.publish_bit(project, 'cpm-hub.zip')

        http_client.post.assert_called_once_with(
            connector.repository_url,
            data='{"bit_name": "cpm-hub", "version": "0.1", "payload": "Yml0IHBheWxvYWQ=", "username": "username", "password": "password"}'
        )

    @patch('cpm.infrastructure.cpm_hub_connector_v1.filesystem')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_bit_raises_authentication_error_on_status_code_401(self, getpass, input, http_client, filesystem):
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1()
        http_client.post.return_value = HttpResponse(401, '')
        filesystem.read_file.return_value = b'bit payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        self.assertRaises(AuthenticationFailure, connector.publish_bit, project, 'cpm-hub.zip')

    @patch('cpm.infrastructure.cpm_hub_connector_v1.filesystem')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_bit_raises_invalid_cpm_hub_url_on_status_code_404(self, getpass, input, http_client, filesystem):
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1()
        http_client.post.return_value = HttpResponse(404, '')
        filesystem.read_file.return_value = b'bit payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        self.assertRaises(InvalidCpmHubUrl, connector.publish_bit, project, 'cpm-hub.zip')

    @patch('cpm.infrastructure.cpm_hub_connector_v1.filesystem')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_bit_raises_publication_error_when_status_code_is_not_200(self, getpass, input, http_client, filesystem):
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1()
        http_client.post.return_value = HttpResponse(409, '')
        filesystem.read_file.return_value = b'bit payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        self.assertRaises(PublicationFailure, connector.publish_bit, project, 'cpm-hub.zip')

    @patch('cpm.infrastructure.cpm_hub_connector_v1.filesystem')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_bit_gets_bit_with_base64_encoded_payload(self, http_client, filesystem):
        connector = CpmHubConnectorV1()
        http_client.get.return_value = HttpResponse(HTTPStatus.OK, '{"bit_name": "cpm-hub", "version": "0.1", "payload": "Yml0IHBheWxvYWQ="}')

        bit_download = connector.download_bit('cest', 'latest')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest')
        assert bit_download == BitDownload("cpm-hub", "0.1", "Yml0IHBheWxvYWQ=")

    @patch('cpm.infrastructure.cpm_hub_connector_v1.filesystem')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_bit_gets_bit_with_specific_version(self, http_client, filesystem):
        connector = CpmHubConnectorV1()
        http_client.get.return_value = HttpResponse(HTTPStatus.OK, '{"bit_name": "cpm-hub", "version": "1.0", "payload": "Yml0IHBheWxvYWQ="}')

        bit_download = connector.download_bit('cest', '1.0')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest/1.0')
        assert bit_download == BitDownload("cpm-hub", "1.0", "Yml0IHBheWxvYWQ=")

    @patch('cpm.infrastructure.cpm_hub_connector_v1.filesystem')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_bit_raises_exception_when_bit_is_not_found(self, http_client, filesystem):
        connector = CpmHubConnectorV1()
        http_client.get.return_value = HttpResponse(HTTPStatus.NOT_FOUND, '')

        self.assertRaises(BitNotFound, connector.download_bit, 'cest', 'latest')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest')
