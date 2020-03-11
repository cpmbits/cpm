import json
import unittest
from mock import patch, MagicMock

from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.domain.project import Project


class TestCpmHubConnectorV1(unittest.TestCase):
    @patch('cpm.infrastructure.http_client.post')
    @patch('cpm.infrastructure.cpm_hub_connector_v1.base64')
    def test_plugin_publication(self, base64, http_post):
        filesystem = MagicMock()
        connector = CpmHubConnectorV1(filesystem, repository_url='my.url.com')
        project = Project('cest')
        binary_encoded = MagicMock()
        binary_encoded.decode.return_value = 'ABCDE'
        base64.b64encode.return_value = binary_encoded
        filesystem.read_file.return_value = 'fafa'

        connector.publish_plugin(project, 'cest.zip')

        http_post.assert_called_once_with(
            'my.url.com',
            data=json.dumps({
                'plugin_name': 'cest',
                'version': '0.1',
                'payload': 'ABCDE',
            })
        )
