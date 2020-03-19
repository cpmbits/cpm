import unittest
import mock

from cpm.domain.clean_service import CleanService
from cpm.domain.cmake_recipe import BUILD_DIRECTORY
from cpm.domain.project_loader import NotAChromosProject


class TestCleanService(unittest.TestCase):
    def test_clean_service_creation(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        CleanService(filesystem, project_loader)

    def test_clean_service_fails_when_project_loader_fails_to_load_project(self):
        filesystem = mock.MagicMock()
        project_loader = mock.MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = CleanService(filesystem, project_loader)

        self.assertRaises(NotAChromosProject, service.clean)

        project_loader.load.assert_called_once()

    def test_clean_service_remove_recipes_directory_from_project(self):
        filesystem = mock.MagicMock()
        filesystem.directory_exists.return_value = True
        project_loader = mock.MagicMock()
        service = CleanService(filesystem, project_loader)

        service.clean()

        project_loader.load.assert_called_once()
        filesystem.remove_directory.assert_called_once_with(BUILD_DIRECTORY)

    def test_clean_service_skips_when_recipes_directory_does_not_exist(self):
        filesystem = mock.MagicMock()
        filesystem.directory_exists.return_value = False
        project_loader = mock.MagicMock()
        service = CleanService(filesystem, project_loader)

        service.clean()

        project_loader.load.assert_called_once()
        filesystem.remove_directory.assert_not_called()
