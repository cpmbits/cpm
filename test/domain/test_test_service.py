import unittest
import mock

from cpm.domain.project import Project
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.test_service import TestService, NoTestsFound


class TestTestService(unittest.TestCase):
    def test_service_creation(self):
        project_loader = mock.MagicMock()
        TestService(project_loader)

    def test_service_fails_when_project_loader_fails_to_load_project(self):
        test_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = TestService(project_loader)

        self.assertRaises(NotAChromosProject, service.run_tests, test_recipe)

        project_loader.load.assert_called_once()

    def test_service_raises_exception_when_no_test_suites_are_found(self):
        test_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project = Project('ProjectName')
        project_loader.load.return_value = project
        service = TestService(project_loader)

        self.assertRaises(NoTestsFound, service.run_tests, test_recipe)

        project_loader.load.assert_called_once()
        test_recipe.generate.assert_not_called()
        test_recipe.compile.assert_not_called()
        test_recipe.run_tests.assert_not_called()

    def test_service_generates_the_recipe_then_compiles_and_runs_the_tests(self):
        test_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project = Project('ProjectName')
        project.tests = ['test']
        project_loader.load.return_value = project
        service = TestService(project_loader)

        service.run_tests(test_recipe)

        project_loader.load.assert_called_once()
        test_recipe.generate.assert_called_once_with(project)
        test_recipe.compile.assert_called_once_with(project)
        test_recipe.run_tests.assert_called_once_with(project)

