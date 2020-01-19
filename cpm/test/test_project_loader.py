import unittest
import mock

from cpm.domain import project_loader
from cpm.domain import project
from cpm.domain import target


class TestProjectLoader(unittest.TestCase):
    def test_project_loader_creation(self):
        yaml_handler = mock.MagicMock()
        project_loader.ProjectLoader(yaml_handler)

    def test_loading_project_raises_exception_when_project_descriptor_does_not_exist(self):
        yaml_handler = mock.MagicMock()
        yaml_handler.load.side_effect = FileNotFoundError()
        loader = project_loader.ProjectLoader(yaml_handler)

        self.assertRaises(project_loader.NotAChromosProject, loader.load)

    def test_loading_project_without_targets(self):
        yaml_handler = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project'
        }
        loader = project_loader.ProjectLoader(yaml_handler)

        loaded_project = loader.load()

        yaml_handler.load.assert_called_once_with(project.ROOT_FILE)
        assert loaded_project.name == 'Project'

    def test_loading_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project',
            'targets': {
                'ubuntu': {},
            }
        }
        loader = project_loader.ProjectLoader(yaml_handler)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert 'ubuntu' in loaded_project.targets

    def test_saving_project_without_targets(self):
        yaml_handler = mock.MagicMock()
        test_project = project.Project('Project')
        loader = project_loader.ProjectLoader(yaml_handler)

        loader.save(test_project)

        yaml_handler.dump.assert_called_once_with(
            project.ROOT_FILE,
            {'project_name': 'Project'}
        )

    def test_saving_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        test_project = project.Project('Project')
        test_project.add_target(target.Target('ubuntu'))
        loader = project_loader.ProjectLoader(yaml_handler)

        loader.save(test_project)

        yaml_handler.dump.assert_called_once_with(
            project.ROOT_FILE,
            {
                'project_name': 'Project',
                'targets': {'ubuntu': {}}
            }
        )
