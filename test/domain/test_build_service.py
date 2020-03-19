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
        cmake_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = BuildService(project_loader)

        self.assertRaises(NotAChromosProject, service.build, cmake_recipe)
        self.assertRaises(NotAChromosProject, service.update, cmake_recipe)
        project_loader.load.assert_called()

    def test_build_service_generates_compilation_recipe_from_project_sources_and_compiles_project(self):
        cmake_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        service = BuildService(project_loader)
        project = Project('ProjectName')
        project_loader.load.return_value = project

        service.build(cmake_recipe)

        project_loader.load.assert_called_once()
        cmake_recipe.generate.assert_called_once_with(project)
        cmake_recipe.build.assert_called_once_with(project)

    def test_build_service_only_generates_compilation_recipe_when_updating(self):
        cmake_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project = Project('ProjectName')
        project_loader.load.return_value = project
        service = BuildService(project_loader)

        service.update(cmake_recipe)

        project_loader.load.assert_called_once()
        cmake_recipe.generate.assert_called_once_with(project)

    def test_clean_fails_when_project_loader_fails_to_load_project(self):
        cmake_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = BuildService(project_loader)

        self.assertRaises(NotAChromosProject, service.clean, cmake_recipe)

        project_loader.load.assert_called_once()

    def test_clean_uses_cmake_recipe_to_clean_project(self):
        cmake_recipe = mock.MagicMock()
        project_loader = mock.MagicMock()
        service = BuildService(project_loader)

        service.clean(cmake_recipe)

        project_loader.load.assert_called_once()
        cmake_recipe.clean.assert_called_once()

