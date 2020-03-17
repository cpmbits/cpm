import unittest

from mock import MagicMock
from mock import patch

from cpm.api.project_actions import discover_project_actions
from cpm.domain.project import Project, ProjectAction
from cpm.domain.project_loader import NotAChromosProject
from cpm.infrastructure.project_action_runner import ProjectActionRunner


class TestApiProjectActions(unittest.TestCase):
    @patch("cpm.api.project_actions.ProjectLoader")
    def test_project_actions_discovers_zero_actions_when_current_directory_is_not_a_cpm_project(self, ProjectLoader):
        project_loader = MagicMock()
        ProjectLoader.return_value = project_loader
        project_loader.load.side_effect = NotAChromosProject
        assert discover_project_actions() == []

    @patch("cpm.api.project_actions.ProjectLoader")
    def test_project_actions_discovers_zero_actions_when_project_has_no_actions(self, ProjectLoader):
        project_loader = MagicMock()
        ProjectLoader.return_value = project_loader
        project_loader.load.return_value = Project("cpm-hub")
        assert discover_project_actions() == []

    @patch("cpm.api.project_actions.ProjectLoader")
    def test_project_actions_discovers_one_action_when_project_has_one_actions(self, ProjectLoader):
        project_loader = MagicMock()
        ProjectLoader.return_value = project_loader
        project = Project("cpm-hub")
        project.add_action(ProjectAction("deploy", "sudo make me a sandwich"))
        project_loader.load.return_value = project
        assert discover_project_actions() == [ProjectActionRunner("deploy", "sudo make me a sandwich")]
