import unittest
import mock

from cpm.domain.project_loader import ProjectLoader
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project import Project, Package, ProjectAction
from cpm.domain.plugin import Plugin
from cpm.domain.project import PROJECT_ROOT_FILE
from cpm.domain.target import Target


class TestProjectLoader(unittest.TestCase):
    def test_creating_project_loader(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        ProjectLoader(yaml_handler, filesystem)

    def test_loading_project_raises_exception_when_project_descriptor_does_not_exist(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.side_effect = FileNotFoundError()
        loader = ProjectLoader(yaml_handler, filesystem)

        self.assertRaises(NotAChromosProject, loader.load)

    def test_loading_project(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project'
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        yaml_handler.load.assert_called_once_with(PROJECT_ROOT_FILE)
        assert loaded_project.name == 'Project'

    def test_loading_project_with_specified_version(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'version': '1.5'
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        yaml_handler.load.assert_called_once_with(PROJECT_ROOT_FILE)
        assert loaded_project.name == 'Project'
        assert loaded_project.version == '1.5'

    def test_loading_project_with_one_package(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        filesystem.parent_directory.return_value = '.'
        yaml_handler.load.return_value = {
            'name': 'Project',
            'packages': {'cpm-hub': None},
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert project.name == 'Project'
        assert Package(path='cpm-hub') in project.packages
        assert project.include_directories == ['.']

    def test_loading_project_with_one_package_with_cflags(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        yaml_handler.load.return_value = {
            'name': 'Project',
            'packages': {
                'cpm-hub': {
                    'cflags': ['-std=c++11']
                }
            },
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert Package(path='cpm-hub', cflags=['-std=c++11']) in project.packages

    def test_loading_project_with_with_ldflags(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        yaml_handler.load.return_value = {
            'name': 'Project',
            'link_options': {
                'libraries': ['pthread']
            },
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert 'pthread' in project.link_options.libraries

    def test_loading_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'targets': {
                'ubuntu': {},
            }
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert 'ubuntu' in loaded_project.targets

    @mock.patch('cpm.domain.project_loader.PluginLoader')
    def test_loading_project_with_one_plugin(self, PluginLoader):
        filesystem = mock.MagicMock()
        plugin_loader = mock.MagicMock()
        PluginLoader.return_value = plugin_loader
        yaml_handler = mock.MagicMock()
        yaml_handler.load.return_value = {'name': 'Project'}
        loader = ProjectLoader(yaml_handler, filesystem)

        filesystem.list_directories.return_value = ['cest']
        plugin = Plugin('cest')
        plugin.add_include_directory('plugins/cest')
        plugin_loader.load_from.return_value = plugin

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.plugins == [Plugin('cest')]
        assert loaded_project.include_directories == ['plugins/cest']

    def test_loading_package_with_sources(self):
        filesystem = mock.MagicMock()
        filesystem.find.side_effect = [['package/file.cpp'], ['package/file.c']]
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)

        package = loader.load_package('package', {})

        assert package == Package(path='package', sources=['package/file.cpp', 'package/file.c'])
        filesystem.find.assert_has_calls([
            mock.call('package', '*.cpp'),
            mock.call('package', '*.c'),
        ])

    def test_finding_project_test_suites(self):
        filesystem = mock.MagicMock()
        filesystem.find.return_value = ['tests/test_project.cpp']
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)

        tests = loader.test_suites()

        assert tests == ['tests/test_project.cpp']
        filesystem.find.assert_called_once_with('tests', 'test_*.cpp')

    def test_loading_local_plugins_when_plugins_directory_is_empty(self):
        filesystem = mock.MagicMock()
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)
        filesystem.list_directories.return_value = []

        plugins = loader.load_local_plugins()

        assert plugins == []
        filesystem.list_directories.assert_called_once_with('plugins')

    @mock.patch('cpm.domain.project_loader.PluginLoader')
    def test_loading_local_plugins_when_plugins_directory_contains_one_plugin(self, PluginLoader):
        filesystem = mock.MagicMock()
        yaml_handler = mock.MagicMock()
        plugin_loader = mock.MagicMock()
        PluginLoader.return_value = plugin_loader
        loader = ProjectLoader(yaml_handler, filesystem)

        filesystem.list_directories.return_value = ['cest']
        plugin_loader.load_from.return_value = Plugin('cest')

        plugins = loader.load_local_plugins()

        assert plugins == [Plugin('cest')]
        filesystem.list_directories.assert_called_once_with('plugins')
        plugin_loader.load_from.assert_called_once_with('plugins/cest')

    @mock.patch('cpm.domain.project_loader.PluginLoader')
    def test_loading_local_plugins_when_plugins_directory_contains_many_plugins(self, PluginLoader):
        filesystem = mock.MagicMock()
        yaml_handler = mock.MagicMock()
        plugin_loader = mock.MagicMock()
        PluginLoader.return_value = plugin_loader
        loader = ProjectLoader(yaml_handler, filesystem)

        filesystem.list_directories.return_value = ['cest', 'base64']
        plugin_loader.load_from.side_effect = [Plugin('cest'), Plugin('base64')]

        plugins = loader.load_local_plugins()

        assert plugins == [Plugin('cest'), Plugin('base64')]
        filesystem.list_directories.assert_called_once_with('plugins')
        plugin_loader.load_from.assert_has_calls([
            mock.call('plugins/cest'),
            mock.call('plugins/base64')
        ])

    def test_loading_project_with_one_action(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'actions': {
                'deploy': 'sudo make me a sandwich'
            }
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        yaml_handler.load.assert_called_once_with(PROJECT_ROOT_FILE)
        assert loaded_project.name == 'Project'
        assert loaded_project.actions == [ProjectAction('deploy', 'sudo make me a sandwich')]

