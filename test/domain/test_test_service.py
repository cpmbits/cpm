import unittest
import mock

from cpm.domain.project.project import Project
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound
from cpm.domain.test_service import TestService, NoTestsFound


class TestTestService(unittest.TestCase):
    def setUp(self):
        self.cmakelists_builder = mock.MagicMock()
        self.project_loader = mock.MagicMock()
        self.project_commands = mock.MagicMock()
        self.test_service = TestService(self.project_loader, self.cmakelists_builder, self.project_commands)

    def test_service_fails_when_project_loader_fails_to_load_project(self):
        self.project_loader.load.side_effect = ProjectDescriptorNotFound

        self.assertRaises(ProjectDescriptorNotFound, self.test_service.run_tests, [], 'default')

        self.project_loader.load.assert_called_once()

    def test_service_raises_exception_when_no_test_suites_are_found(self):
        project = Project('ProjectName')
        self.project_loader.load.return_value = project

        self.assertRaises(NoTestsFound, self.test_service.run_tests, [], 'default')

        self.project_loader.load.assert_called_once()

    def test_service_generates_the_recipe_then_compiles_and_runs_the_tests(self):
        project = Project('ProjectName')
        project.test.test_suites = ['test']
        self.project_loader.load.return_value = project

        self.test_service.run_tests([], 'default')

        self.project_loader.load.assert_called_once()
        self.cmakelists_builder.build.assert_called_once_with(project)
        self.project_commands.build_tests.assert_called_once_with(project, [])
        self.project_commands.run_tests.assert_called_once_with(project, [], ())

    def test_service_build_and_runs_only_specified_tests(self):
        project = Project('ProjectName')
        project.test.test_suites = ['test']
        self.project_loader.load.return_value = project

        self.test_service.run_tests(['tests'], 'default')

        self.project_loader.load.assert_called_once()
        self.cmakelists_builder.build.assert_called_once_with(project)
        self.project_commands.build_tests.assert_called_once_with(project, ['tests'])
        self.project_commands.run_tests.assert_called_once_with(project, ['tests'], ())

    def test_service_passes_test_args_to_run_command(self):
        project = Project('ProjectName')
        project.test.test_suites = ['test']
        self.project_loader.load.return_value = project

        self.test_service.run_tests(['tests'], 'default', test_args=['arg1'])

        self.project_loader.load.assert_called_once()
        self.cmakelists_builder.build.assert_called_once_with(project)
        self.project_commands.build_tests.assert_called_once_with(project, ['tests'])
        self.project_commands.run_tests.assert_called_once_with(project, ['tests'], ['arg1'])
