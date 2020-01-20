import unittest
import mock

from cpm.domain.project_loader import ProjectLoader
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project import Project
from cpm.domain.project import PROJECT_ROOT_FILE
from cpm.domain.target import Target


class TestProjectLoader(unittest.TestCase):
    def test_project_loader_creation(self):
        yaml_handler = mock.MagicMock()
        ProjectLoader(yaml_handler)

    def test_loading_project_raises_exception_when_project_descriptor_does_not_exist(self):
        yaml_handler = mock.MagicMock()
        yaml_handler.load.side_effect = FileNotFoundError()
        loader = ProjectLoader(yaml_handler)

        self.assertRaises(NotAChromosProject, loader.load)

    def test_loading_project_without_targets(self):
        yaml_handler = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project'
        }
        loader = ProjectLoader(yaml_handler)

        loaded_project = loader.load()

        yaml_handler.load.assert_called_once_with(PROJECT_ROOT_FILE)
        assert loaded_project.name == 'Project'

    def test_loading_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project',
            'targets': {
                'ubuntu': {},
            }
        }
        loader = ProjectLoader(yaml_handler)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert 'ubuntu' in loaded_project.targets

    def test_saving_project_without_targets(self):
        yaml_handler = mock.MagicMock()
        test_project = Project('Project')
        loader = ProjectLoader(yaml_handler)

        loader.save(test_project)

        yaml_handler.dump.assert_called_once_with(
            PROJECT_ROOT_FILE,
            {'project_name': 'Project'}
        )

    def test_saving_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        test_project = Project('Project')
        test_project.add_target(Target('ubuntu'))
        loader = ProjectLoader(yaml_handler)

        loader.save(test_project)

        yaml_handler.dump.assert_called_once_with(
            PROJECT_ROOT_FILE,
            {
                'project_name': 'Project',
                'targets': {'ubuntu': {}}
            }
        )
