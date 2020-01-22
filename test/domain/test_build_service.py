import unittest
import mock


from cpm.domain.build_service import BuildService
from cpm.domain.project import Project
from cpm.domain.project_loader import NotAChromosProject


class TestBuildService(unittest.TestCase):
    def test_build_service_creation(self):
        project_loader = mock.MagicMock()
        BuildService(project_loader)

    def test_build_service_fails_when_project_loader_fails_to_load_project(self):
        compilation_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = BuildService(project_loader)

        self.assertRaises(NotAChromosProject, service.build, compilation_recipe)

        project_loader.load.assert_called_once()

    def test_build_service_generates_compilation_recipe_from_project_sources_and_compiles_project(self):
        compilation_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project = Project('ProjectName')
        project_loader.load.return_value = project
        service = BuildService(project_loader)

        service.build(compilation_recipe)

        project_loader.load.assert_called_once()
        compilation_recipe.generate.assert_called_once_with(project)
        compilation_recipe.compile.assert_called_once_with(project)
