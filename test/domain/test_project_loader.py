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
        filesystem = mock.MagicMock()
        ProjectLoader(yaml_handler, filesystem)

    def test_loading_project_raises_exception_when_project_descriptor_does_not_exist(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.side_effect = FileNotFoundError()
        loader = ProjectLoader(yaml_handler, filesystem)

        self.assertRaises(NotAChromosProject, loader.load)

    def test_loading_project_without_targets(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project'
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        yaml_handler.load.assert_called_once_with(PROJECT_ROOT_FILE)
        assert loaded_project.name == 'Project'

    def test_loading_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project',
            'targets': {
                'ubuntu': {},
            }
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert 'ubuntu' in loaded_project.targets

    def test_loading_project_with_one_source_file(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {'project_name': 'Project'}
        filesystem.find.side_effect = [['sources/main.cpp'], [], [], []]
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.sources == ['sources/main.cpp']
        filesystem.find.assert_has_calls([
            mock.call('sources', '*.cpp'),
            mock.call('sources', '*.c'),
        ])

    def test_loading_project_with_one_plugin(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project',
            'plugins': {'cest': {}}
        }
        filesystem.find.side_effect = [
            ['sources/main.cpp'], [],
            ['plugins/cest/sources/cest.cpp'], [],
        ]
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.sources == ['sources/main.cpp', 'plugins/cest/sources/cest.cpp']

    def test_saving_project_without_targets(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        test_project = Project('Project')
        loader = ProjectLoader(yaml_handler, filesystem)

        loader.save(test_project)

        yaml_handler.dump.assert_called_once_with(
            PROJECT_ROOT_FILE,
            {'project_name': 'Project'}
        )

    def test_saving_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        test_project = Project('Project')
        test_project.add_target(Target('ubuntu'))
        loader = ProjectLoader(yaml_handler, filesystem)

        loader.save(test_project)

        yaml_handler.dump.assert_called_once_with(
            PROJECT_ROOT_FILE,
            {
                'project_name': 'Project',
                'targets': {'ubuntu': {}}
            }
        )
