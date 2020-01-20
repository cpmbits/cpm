import unittest
import mock

from cpm.api.target import add_target
from cpm.domain.project_loader import NotAChromosProject


class TestApiTarget(unittest.TestCase):
    def test_add_target_fails_when_directory_is_not_a_chromos_project(self):
        target_service = mock.MagicMock()
        target_service.add_target.side_effect = NotAChromosProject()

        result = add_target(target_service, 'ubuntu-latest')

        assert result.status_code == 1
        target_service.add_target.assert_called_once_with('ubuntu-latest')

    def test_add_target_to_chromos_project(self):
        target_service = mock.MagicMock()

        result = add_target(target_service, 'ubuntu-latest')

        assert result.status_code == 0
        target_service.add_target.assert_called_once_with('ubuntu-latest')

