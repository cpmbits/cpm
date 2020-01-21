import unittest
import mock

from cpm.api.build import build_project
from cpm.domain.project_loader import NotAChromosProject


class TestApiBuild(unittest.TestCase):
    def test_build_fails_when_current_directory_is_not_a_chromos_project(self):
        recipe = mock.MagicMock()
        build_service = mock.MagicMock()
        build_service.build.side_effect = NotAChromosProject()

        result = build_project(build_service, recipe)

        assert result.status_code == 1
        build_service.build.assert_called_once_with(recipe)

    def test_build_project(self):
        build_service = mock.MagicMock()
        recipe = mock.MagicMock()

        result = build_project(build_service, recipe)

        assert result.status_code == 0
        build_service.build.assert_called_once_with(recipe)
