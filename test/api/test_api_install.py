import unittest
import mock

from cpm.api.install import install_plugin
from cpm.domain.install_service import PluginNotFound
from cpm.domain.project_loader import NotAChromosProject


class TestApiInstall(unittest.TestCase):
    def test_plugin_install_fails_when_current_directory_is_not_a_chromos_project(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = NotAChromosProject

        result = install_plugin(install_service, "cest")

        assert result.status_code == 1
        install_service.install.assert_called_once_with("cest")

    def test_plugin_install_fails_when_plugin_is_not_found(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = PluginNotFound

        result = install_plugin(install_service, "cest")

        assert result.status_code == 1
        install_service.install.assert_called_once_with("cest")
