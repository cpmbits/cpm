import unittest
import mock

from cpm.domain.target_service import TargetService
from cpm.domain.target import Target
from cpm.domain.project_loader import NotAChromosProject


class TestTargetService(unittest.TestCase):
    def test_target_service_creation(self):
        project_loader = mock.MagicMock()
        TargetService(project_loader)

    def test_target_service_raises_exception_adding_target_when_project_loader_fails(self):
        project_loader = mock.MagicMock()
        service = TargetService(project_loader)
        project_loader.load.side_effect = NotAChromosProject

        self.assertRaises(NotAChromosProject, service.add_target, 'ubuntu-latest')

    def test_target_service_adds_target_to_project(self):
        project_loader = mock.MagicMock()
        project = mock.MagicMock()
        service = TargetService(project_loader)
        project_loader.load.return_value = project

        service.add_target('ubuntu-latest')

        project_loader.load.assert_called_once()
        project.add_target.assert_called_once_with(Target('ubuntu-latest'))
        project_loader.save.assert_called_once_with(project)
