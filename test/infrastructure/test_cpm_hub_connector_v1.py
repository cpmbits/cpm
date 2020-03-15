import unittest
from mock import patch
from mock import MagicMock

from http import HTTPStatus

from cpm.domain.install_service import PluginNotFound
from cpm.domain.plugin_download import PluginDownload
from cpm.domain.project import Project
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.http_client import HttpResponse


class TestCpmHubConnectorV1(unittest.TestCase):
    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_publish_plugin_posts_plugin_with_base64_encoded_payload(self, http_client):
        filesystem = MagicMock()
        project = Project('cpm-hub')
        connector = CpmHubConnectorV1(filesystem)
        filesystem.read_file.return_value = b'plugin payload'

        connector.publish_plugin(project, 'cpm-hub.zip')

        http_client.post.assert_called_once_with(
            connector.repository_url,
            data='{"plugin_name": "cpm-hub", "version": "0.1", "payload": "cGx1Z2luIHBheWxvYWQ="}'
        )

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_plugin_gets_plugin_with_base64_encoded_payload(self, http_client):
        filesystem = MagicMock()
        connector = CpmHubConnectorV1(filesystem)
        http_client.get.return_value = HttpResponse(HTTPStatus.OK, '{"plugin_name": "cpm-hub", "version": "0.1", "payload": "cGx1Z2luIHBheWxvYWQ="}')

        plugin_download = connector.download_plugin('cest')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest')
        assert plugin_download == PluginDownload("cpm-hub", "0.1", "cGx1Z2luIHBheWxvYWQ=")

    @patch('cpm.infrastructure.cpm_hub_connector_v1.http_client')
    def test_download_plugin_raises_exception_when_plugin_is_not_found(self, http_client):
        filesystem = MagicMock()
        connector = CpmHubConnectorV1(filesystem)
        http_client.get.return_value = HttpResponse(HTTPStatus.NOT_FOUND, '')

        self.assertRaises(PluginNotFound, connector.download_plugin, 'cest')

        http_client.get.assert_called_once_with(f'{connector.repository_url}/cest')
