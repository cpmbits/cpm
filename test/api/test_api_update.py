import unittest
import mock

from cpm.api.update import update_project
from cpm.domain.project_loader import NotAChromosProject


class TestApiUpdate(unittest.TestCase):
    def test_update_fails_when_current_directory_is_not_a_chromos_project(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()
        compilation_service.update.side_effect = NotAChromosProject()

        result = update_project(compilation_service, recipe)

        assert result.status_code == 1
        compilation_service.update.assert_called_once()

    def test_update_project(self):
        recipe = mock.MagicMock()
        compilation_service = mock.MagicMock()

        result = update_project(compilation_service, recipe)

        assert result.status_code == 0
        compilation_service.update.assert_called_once()
