import unittest
import mock

from cpm.domain.project_loader import ProjectLoader
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project import Project, Plugin
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

    def test_loading_project_with_one_plugin(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'project_name': 'Project',
            'plugins': {'cest': {}}
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.plugins == [Plugin('cest', {})]

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

    def test_saving_project_with_one_plugin(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        test_project = Project('Project')
        test_project.add_plugin(Plugin('cest', {}))
        loader = ProjectLoader(yaml_handler, filesystem)

        loader.save(test_project)

        yaml_handler.dump.assert_called_once_with(
            PROJECT_ROOT_FILE,
            {
                'project_name': 'Project',
                'plugins': {'cest': {}}
            }
        )

    def test_finding_project_sources(self):
        filesystem = mock.MagicMock()
        filesystem.find.side_effect = [['sources/main.cpp'], ['source.c']]
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)

        sources = loader.project_sources()

        assert sources == ['sources/main.cpp', 'source.c']
        filesystem.find.assert_has_calls([
            mock.call('sources', '*.cpp'),
            mock.call('sources', '*.c'),
        ])

    def test_finding_plugin_sources(self):
        filesystem = mock.MagicMock()
        filesystem.find.side_effect = [['plugin.cpp'], ['plugin.c']]
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)
        plugins = [Plugin('cest', {})]

        sources = loader.plugin_sources(plugins)

        assert sources == ['plugin.cpp', 'plugin.c']
        filesystem.find.assert_has_calls([
            mock.call('plugins/cest/sources', '*.cpp'),
            mock.call('plugins/cest/sources', '*.c'),
        ])

    def test_finding_project_test_suites(self):
        filesystem = mock.MagicMock()
        filesystem.find.return_value = ['tests/test_project.cpp']
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)

        tests = loader.test_suites()

        assert tests == ['tests/test_project.cpp']
        filesystem.find.assert_called_once_with('tests', 'test_*.cpp')
