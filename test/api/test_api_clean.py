import unittest
from mock import MagicMock

from cpm.api.clean import clean_project
from cpm.domain.project_loader import NotAChromosProject


class TestApiClean(unittest.TestCase):
    def test_clean_fails_when_current_directory_is_not_a_chromos_project(self):
        cmake_recipe = MagicMock()
        compilation_service = MagicMock()
        compilation_service.clean.side_effect = NotAChromosProject()

        result = clean_project(compilation_service, cmake_recipe)

        assert result.status_code == 1
        compilation_service.clean.assert_called_once_with(cmake_recipe)

    def test_clean_project(self):
        cmake_recipe = MagicMock()
        compilation_service = MagicMock()

        result = clean_project(compilation_service, cmake_recipe)

        assert result.status_code == 0
        compilation_service.clean.assert_called_once_with(cmake_recipe)
