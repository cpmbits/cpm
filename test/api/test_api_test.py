import unittest
import mock

from cpm.api.test import run_tests
from cpm.domain.project_commands import BuildError
from cpm.domain.project.project_descriptor_parser import NotACpmProject
from cpm.domain.project_commands import TestsFailed
from cpm.domain.test_service import NoTestsFound


class TestApiTest(unittest.TestCase):
    def test_run_tests_fails_when_current_directory_is_not_a_chromos_project(self):
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = NotACpmProject()

        result = run_tests(test_service)

        assert result.status_code == 1
        test_service.run_tests.assert_called_once_with([], 'default')

    def test_run_tests_fails_when_no_tests_are_found(self):
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = NoTestsFound()

        result = run_tests(test_service)

        assert result.status_code == 0
        test_service.run_tests.assert_called_once_with([], 'default')

    def test_run_tests_fails_when_compilation_fails(self):
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = BuildError()

        result = run_tests(test_service)

        assert result.status_code == 1
        test_service.run_tests.assert_called_once_with([], 'default')

    def test_run_tests_fails_when_tests_fail(self):
        test_service = mock.MagicMock()
        test_service.run_tests.side_effect = TestsFailed()

        result = run_tests(test_service)

        assert result.status_code == 1
        test_service.run_tests.assert_called_once_with([], 'default')

    def test_run_project_tests(self):
        test_service = mock.MagicMock()

        result = run_tests(test_service)

        assert result.status_code == 0
        test_service.run_tests.assert_called_once_with([], 'default')

    def test_run_project_tests_with_patterns(self):
        test_service = mock.MagicMock()

        result = run_tests(test_service, files_or_dirs=['tests'])

        assert result.status_code == 0
        test_service.run_tests.assert_called_once_with(['tests'], 'default')

    def test_run_project_tests_with_target_other_than_default(self):
        test_service = mock.MagicMock()

        result = run_tests(test_service, target='rpi4')

        assert result.status_code == 0
        test_service.run_tests.assert_called_once_with([], 'rpi4')
