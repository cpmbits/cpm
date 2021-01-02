import unittest
from unittest import mock

from cpm.domain.bit_packager import PackagingFailure
from cpm.domain.project.project_descriptor_parser import NotACpmProject
from cpm.infrastructure.http_client import HttpConnectionError
from cpm.api.publish import publish_project
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure
from cpm.infrastructure.cpm_hub_connector_v1 import InvalidCpmHubUrl
from cpm.infrastructure.cpm_hub_connector_v1 import PublicationFailure


class TestApiPublish(unittest.TestCase):
    def test_publish_fails_when_current_directory_is_not_a_chromos_project(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = NotACpmProject

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_fails_when_project_contains_no_packages(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = PackagingFailure

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_fails_when_connection_to_server_fails(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = HttpConnectionError

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_fails_when_invalid_url_is_specified(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = InvalidCpmHubUrl

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_fails_when_authentication_fails(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = AuthenticationFailure

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_fails_when_publication_fails(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = PublicationFailure

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_fails_when_user_interrupts_with_ctrl_c(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = KeyboardInterrupt

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_api(self):
        publish_service = mock.MagicMock()

        result = publish_project(publish_service)

        assert result.status_code == 0
