import unittest
import mock

from cpm.api.clean import clean_project
from cpm.domain.project_loader import NotAChromosProject


class TestApiBuild(unittest.TestCase):
    def test_clean_fails_when_current_directory_is_not_a_chromos_project(self):
        clean_service = mock.MagicMock()
        clean_service.clean.side_effect = NotAChromosProject()

        result = clean_project(clean_service)

        assert result.status_code == 1
        clean_service.clean.assert_called_once()

    def test_clean_project(self):
        clean_service = mock.MagicMock()

        result = clean_project(clean_service)

        assert result.status_code == 0
        clean_service.clean.assert_called_once()
