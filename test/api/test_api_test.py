import unittest
import mock

from cpm.api.test import run_tests
from cpm.domain.cmake_recipe import CompilationError
from cpm.domain.cmake_recipe import TestsFailed
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.test_service import NoTestsFound


class TestApiTest(unittest.TestCase):
    def test_run_tests_fails_when_current_directory_is_not_a_chromos_project(self):
        recipe = mock.MagicMock()
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = NotAChromosProject()

        result = run_tests(test_service, recipe)

        assert result.status_code == 1
        test_service.run_tests.assert_called_once_with(recipe, [])

    def test_run_tests_fails_when_no_tests_are_found(self):
        recipe = mock.MagicMock()
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = NoTestsFound()

        result = run_tests(test_service, recipe)

        assert result.status_code == 0
        test_service.run_tests.assert_called_once_with(recipe, [])

    def test_run_tests_fails_when_compilation_fails(self):
        recipe = mock.MagicMock()
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = CompilationError()

        result = run_tests(test_service, recipe)

        assert result.status_code == 1
        test_service.run_tests.assert_called_once_with(recipe, [])

    def test_run_tests_fails_when_tests_fail(self):
        recipe = mock.MagicMock()
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = TestsFailed()

        result = run_tests(test_service, recipe)

        assert result.status_code == 1
        test_service.run_tests.assert_called_once_with(recipe, [])

    def test_run_project_tests(self):
        recipe = mock.MagicMock()
        test_service = mock.MagicMock()

        result = run_tests(test_service, recipe)

        assert result.status_code == 0
        test_service.run_tests.assert_called_once_with(recipe, [])

    def test_run_project_tests_with_patterns(self):
        recipe = mock.MagicMock()
        test_service = mock.MagicMock()

        result = run_tests(test_service, recipe, patterns=['test_pattern'])

        assert result.status_code == 0
        test_service.run_tests.assert_called_once_with(recipe, ['test_pattern'])
