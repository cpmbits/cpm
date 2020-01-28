import unittest
from mock import MagicMock
from mock import call

from cpm.domain.plugin_loader import PluginLoader


class TestPluginLoader(unittest.TestCase):
    def test_creating_plugin_loader(self):
        yaml_handler = MagicMock()
        filesystem = MagicMock()
        PluginLoader(yaml_handler, filesystem)

    def test_loading_simple_plugin_without_cflags_or_packages(self):
        filesystem = MagicMock()
        yaml_handler = MagicMock()
        yaml_handler.load.return_value = {
            'plugin_name': 'cest'
        }
        loader = PluginLoader(yaml_handler, filesystem)

        plugin = loader.load('cest', '1.0')

        yaml_handler.load.assert_called_once_with('plugins/cest/plugin.yaml')
        assert plugin.name == 'cest'
        assert plugin.include_directories == ['plugins/cest']

    def test_finding_plugin_sources(self):
        filesystem = MagicMock()
        filesystem.find.side_effect = [['plugin.cpp'], ['plugin.c']]
        yaml_handler = MagicMock()
        loader = PluginLoader(yaml_handler, filesystem)

        sources = loader.plugin_sources('cest')

        assert sources == ['plugin.cpp', 'plugin.c']
        filesystem.find.assert_has_calls([
            call('plugins/cest/sources', '*.cpp'),
            call('plugins/cest/sources', '*.c'),
        ])
