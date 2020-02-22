import unittest
from unittest import mock

from cpm.domain.plugin_packager import PackagingFailure
from cpm.domain.project_loader import NotAChromosProject
from cpm.api.publish import publish_project


class TestApiPublish(unittest.TestCase):
    def test_publish_fails_when_current_directory_is_not_a_chromos_project(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = NotAChromosProject

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_fails_when_project_contains_no_packages(self):
        publish_service = mock.MagicMock()
        publish_service.publish.side_effect = PackagingFailure

        result = publish_project(publish_service)

        assert result.status_code == 1
        publish_service.publish.assert_called_once()

    def test_publish_api(self):
        publish_service = mock.MagicMock()

        result = publish_project(publish_service)

        assert result.status_code == 0
