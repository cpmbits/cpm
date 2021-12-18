import unittest
from mock import MagicMock
from mock import patch

import os

from cpm.domain.compilation_service import CompilationService
from cpm.domain.project_commands import DockerImageNotFound
from cpm.domain.project.project import Project, Target
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound, ParseError


class TestCompilationService(unittest.TestCase):
    def setUp(self):
        self.cmakelists_builder = MagicMock()
        self.project_loader = MagicMock()
        self.project_commands = MagicMock()
        self.compilation_service = CompilationService(self.project_loader, self.cmakelists_builder, self.project_commands)

    def test_compilation_service_fails_when_project_loader_fails_to_load_project(self):
        self.project_loader.load.side_effect = ProjectDescriptorNotFound

        self.assertRaises(ProjectDescriptorNotFound, self.compilation_service.build)
        self.assertRaises(ProjectDescriptorNotFound, self.compilation_service.update)
        self.project_loader.load.assert_called()

    def test_compilation_service_generates_compilation_recipe_from_project_sources_and_compiles_project(self):
        project = Project('ProjectName')
        self.project_loader.load.return_value = project

        self.compilation_service.build('target_name')

        self.project_loader.load.assert_called_once_with('.', 'target_name')
        self.cmakelists_builder.build.assert_called_once_with(project)
        self.project_commands.build.assert_called_once_with(project)

    def test_compilation_service_only_generates_compilation_recipe_when_updating(self):
        project = Project('ProjectName')
        self.project_loader.load.return_value = project

        self.compilation_service.update('target_name')

        self.project_loader.load.assert_called_once_with('.', 'target_name')
        self.cmakelists_builder.build.assert_called_once_with(project)

    def test_clean_fails_when_project_loader_fails_to_load_project(self):
        self.project_loader.load.side_effect = ProjectDescriptorNotFound
        self.assertRaises(ProjectDescriptorNotFound, self.compilation_service.clean)
        self.project_loader.load.assert_called_once()

    def test_clean_uses_project_commands_to_clean_project(self):
        self.compilation_service.clean()

        self.project_loader.load.assert_called_once()
        self.project_commands.clean.assert_called_once()

    def test_clean_ignores_project_descriptor_parsing_errors(self):
        self.project_loader.load.side_effect = ParseError('project.yaml', 1, 1, 'error')

        self.compilation_service.clean()

        self.project_loader.load.assert_called_once()
        self.project_commands.clean.assert_called_once()
