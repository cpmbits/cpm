import unittest
import mock

from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.test_service import TestService


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
