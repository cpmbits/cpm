import unittest
from mock import patch
from mock import MagicMock

from http import HTTPStatus

from cpm.domain.install_service import PluginNotFound
from cpm.domain.plugin_download import PluginDownload
from cpm.domain.project import Project
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure, InvalidCpmHubUrl, PublicationFailure
from cpm.infrastructure.http_client import HttpResponse


class TestCpmHubConnectorV1(unittest.TestCase):
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_plugin_posts_plugin_with_base64_encoded_payload_and_user_credentials(self, getpass, input, http_client):
        filesystem = MagicMock()
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1(filesystem)
        http_client.post.return_value = HttpResponse(200, '')
        filesystem.read_file.return_value = b'plugin payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        connector.publish_plugin(project, 'cpm-hub.zip')

        http_client.post.assert_called_once_with(
            connector.repository_url,
            data='{"plugin_name": "cpm-hub", "version": "0.1", "payload": "cGx1Z2luIHBheWxvYWQ=", "username": "username", "password": "password"}'
        )

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_plugin_raises_authentication_error_on_status_code_401(self, getpass, input, http_client):
        filesystem = MagicMock()
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1(filesystem)
        http_client.post.return_value = HttpResponse(401, '')
        filesystem.read_file.return_value = b'plugin payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        self.assertRaises(AuthenticationFailure, connector.publish_plugin, project, 'cpm-hub.zip')

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_plugin_raises_invalid_cpm_hub_url_on_status_code_404(self, getpass, input, http_client):
        filesystem = MagicMock()
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1(filesystem)
        http_client.post.return_value = HttpResponse(404, '')
        filesystem.read_file.return_value = b'plugin payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        self.assertRaises(InvalidCpmHubUrl, connector.publish_plugin, project, 'cpm-hub.zip')

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    @patch('builtins.input')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.getpass')
    def test_publish_plugin_raises_publication_error_when_status_code_is_not_200(self, getpass, input, http_client):
        filesystem = MagicMock()
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1(filesystem)
        http_client.post.return_value = HttpResponse(409, '')
        filesystem.read_file.return_value = b'plugin payload'
        getpass.return_value = 'password'
        input.return_value = 'username'

        self.assertRaises(PublicationFailure, connector.publish_plugin, project, 'cpm-hub.zip')

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_plugin_gets_plugin_with_base64_encoded_payload(self, http_client):
        filesystem = MagicMock()
        connector = CpmHubConnectorV1(filesystem)
        http_client.get.return_value = HttpResponse(HTTPStatus.OK, '{"plugin_name": "cpm-hub", "version": "0.1", "payload": "cGx1Z2luIHBheWxvYWQ="}')

        plugin_download = connector.download_plugin('cest', 'latest')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest')
        assert plugin_download == PluginDownload("cpm-hub", "0.1", "cGx1Z2luIHBheWxvYWQ=")

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_plugin_gets_plugin_with_specific_version(self, http_client):
        filesystem = MagicMock()
        connector = CpmHubConnectorV1(filesystem)
        http_client.get.return_value = HttpResponse(HTTPStatus.OK, '{"plugin_name": "cpm-hub", "version": "1.0", "payload": "cGx1Z2luIHBheWxvYWQ="}')

        plugin_download = connector.download_plugin('cest', '1.0')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest/1.0')
        assert plugin_download == PluginDownload("cpm-hub", "1.0", "cGx1Z2luIHBheWxvYWQ=")

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_plugin_raises_exception_when_plugin_is_not_found(self, http_client):
        filesystem = MagicMock()
        connector = CpmHubConnectorV1(filesystem)
        http_client.get.return_value = HttpResponse(HTTPStatus.NOT_FOUND, '')

        self.assertRaises(PluginNotFound, connector.download_plugin, 'cest', 'latest')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest')
