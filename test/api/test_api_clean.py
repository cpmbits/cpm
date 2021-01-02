import unittest
from mock import MagicMock

from cpm.api.clean import clean_project
from cpm.domain.project.project_descriptor_parser import NotACpmProject


class TestApiClean(unittest.TestCase):
    def test_clean_fails_when_current_directory_is_not_a_chromos_project(self):
        compilation_service = MagicMock()
        compilation_service.clean.side_effect = NotACpmProject()

        result = clean_project(compilation_service)

        assert result.status_code == 1
        compilation_service.clean.assert_called_once()

    def test_clean_project(self):
        compilation_service = MagicMock()

        result = clean_project(compilation_service)

        assert result.status_code == 0
        compilation_service.clean.assert_called_once()
