import unittest
from mock import MagicMock
from mock import call

from cpm.domain.plugin_loader import PluginLoader
from cpm.domain.project import Package


class TestPluginLoader(unittest.TestCase):
    def test_creating_plugin_loader(self):
        yaml_handler = MagicMock()
        filesystem = MagicMock()
        PluginLoader(yaml_handler, filesystem)

    def test_loading_plugin_without_packages(self):
        filesystem = MagicMock()
        yaml_handler = MagicMock()
        yaml_handler.load.return_value = {
            'plugin_name': 'cest'
        }
        loader = PluginLoader(yaml_handler, filesystem)

        plugin = loader.load('cest', '1.0')

        yaml_handler.load.assert_called_once_with('plugins/cest/plugin.yaml')
        assert plugin.name == 'cest'
        assert plugin.include_directories == []

    def test_loading_plugin_with_one_package(self):
        yaml_handler = MagicMock()
        filesystem = MagicMock()
        filesystem.parent_directory.return_value = 'plugins/cest'
        filesystem.find.side_effect = [['plugins/cest/plugin.cpp'], ['plugins/cest/plugin.c']]
        yaml_handler.load.return_value = {
            'plugin_name': 'cest',
            'packages': {'cest': None},
        }
        loader = PluginLoader(yaml_handler, filesystem)

        plugin = loader.load('cest', '1.0')

        assert plugin.name == 'cest'
        assert Package(path='plugins/cest/cest') in plugin.packages
        assert plugin.include_directories == ['plugins/cest']
        assert plugin.sources == ['plugins/cest/plugin.cpp', 'plugins/cest/plugin.c']

    def test_loading_plugin_with_one_package_with_cflags(self):
        yaml_handler = MagicMock()
        filesystem = MagicMock()
        filesystem.parent_directory.return_value = 'plugins/cest'
        filesystem.find.side_effect = [['plugins/cest/plugin.cpp'], ['plugins/cest/plugin.c']]
        yaml_handler.load.return_value = {
            'plugin_name': 'cest',
            'packages': {
                'cest': {
                    'cflags': ['-std=c++11']
                }
            },
        }
        loader = PluginLoader(yaml_handler, filesystem)

        plugin = loader.load('cest', '1.0')

        assert plugin.name == 'cest'
        assert Package(path='plugins/cest/cest', cflags=['-std=c++11']) in plugin.packages

    def test_finding_plugin_sources(self):
        filesystem = MagicMock()
        filesystem.find.side_effect = [['plugins/cest/plugin.cpp'], ['plugins/cest/plugin.c']]
        yaml_handler = MagicMock()
        loader = PluginLoader(yaml_handler, filesystem)

        sources = loader.plugin_sources([Package('plugins/cest')])

        assert sources == ['plugins/cest/plugin.cpp', 'plugins/cest/plugin.c']
        filesystem.find.assert_has_calls([
            call('plugins/cest', '*.cpp'),
            call('plugins/cest', '*.c'),
        ])
