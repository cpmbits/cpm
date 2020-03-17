import unittest
from mock import patch

from cpm.api.result import Result
from cpm.infrastructure.project_action_runner import ProjectActionRunner


class TestProjectActionRunner(unittest.TestCase):
    @patch("cpm.infrastructure.project_action_runner.os")
    def test_executing_project_action(self, os):
        action_runner = ProjectActionRunner('deploy', 'docker build')
        os.system.return_value = 0

        result = action_runner.execute(None)

        os.system.assert_called_once_with('docker build')
        assert result == Result(0, f'finished "deploy"')
