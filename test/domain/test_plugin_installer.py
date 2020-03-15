import unittest
from mock import MagicMock

from cpm.domain.plugin import Plugin
from cpm.domain.plugin_download import PluginDownload
from cpm.domain.plugin_installer import PluginInstaller


class TestPluginInstaller(unittest.TestCase):
    def test_plugin_installation_when_plugin_was_not_installed_before(self):
        filesystem = MagicMock()
        plugin_loader = MagicMock()
        installer = PluginInstaller(filesystem, plugin_loader)
        plugin_download = PluginDownload("cest", "1.0", "cGx1Z2luIHBheWxvYWQ=")
        plugin_loader.load.return_value = Plugin("cest", "1.0")
        filesystem.directory_exists.return_value = False

        plugin = installer.install(plugin_download)

        filesystem.create_directory.assert_called_once_with('plugins/cest')
        filesystem.unzips.assert_called_once_with(b'plugin payload', 'plugins/cest')
        assert plugin.name == "cest"
        assert plugin.version == "1.0"

    def test_plugin_installation_when_plugin_was_installed_before(self):
        filesystem = MagicMock()
        plugin_loader = MagicMock()
        installer = PluginInstaller(filesystem, plugin_loader)
        plugin_download = PluginDownload("cest", "1.0", "cGx1Z2luIHBheWxvYWQ=")
        plugin_loader.load.return_value = Plugin("cest", "1.0")
        filesystem.directory_exists.return_value = True

        plugin = installer.install(plugin_download)

        filesystem.remove_directory.assert_called_once_with('plugins/cest')
        filesystem.create_directory.assert_called_once_with('plugins/cest')
        filesystem.unzips.assert_called_once_with(b'plugin payload', 'plugins/cest')
        assert plugin.name == "cest"
        assert plugin.version == "1.0"
