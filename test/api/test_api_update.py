import unittest
import mock

from cpm.api.update import update_project
from cpm.domain.project_loader import NotAChromosProject


class TestApiUpdate(unittest.TestCase):
    def test_update_fails_when_current_directory_is_not_a_chromos_project(self):
        recipe = mock.MagicMock()
        build_service = mock.MagicMock()
        build_service.update.side_effect = NotAChromosProject()

        result = update_project(build_service, recipe)

        assert result.status_code == 1
        build_service.update.assert_called_once()

    def test_update_project(self):
        recipe = mock.MagicMock()
        build_service = mock.MagicMock()

        result = update_project(build_service, recipe)

        assert result.status_code == 0
        build_service.update.assert_called_once()
