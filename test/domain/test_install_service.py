import unittest

from mock import MagicMock

from cpm.domain.install_service import InstallService
from cpm.domain.install_service import PluginNotFound
from cpm.domain.plugin import Plugin
from cpm.domain.project import Project
from cpm.domain.project_loader import NotAChromosProject
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure


class TestInstallService(unittest.TestCase):
    def test_install_service_creation(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        InstallService(project_loader, plugin_installer, cpm_hub_connector)

    def test_install_service_fails_when_project_loader_fails_to_load_project(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        project_loader.load.side_effect = NotAChromosProject
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        self.assertRaises(NotAChromosProject, service.install, "cest")

        project_loader.load.assert_called_once()

    def test_install_service_fails_when_authentication_fails(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        cpm_hub_connector.download_plugin.side_effect = AuthenticationFailure
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        self.assertRaises(AuthenticationFailure, service.install, "cest")

        cpm_hub_connector.download_plugin.assert_called_once_with("cest")

    def test_install_service_fails_when_plugin_is_not_found_in_cpm_hub(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        cpm_hub_connector.download_plugin.side_effect = PluginNotFound
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        self.assertRaises(PluginNotFound, service.install, "cest")

        cpm_hub_connector.download_plugin.assert_called_once_with("cest")

    def test_install_service_downloads_plugin_then_installs_it_and_updates_the_project(self):
        project_loader = MagicMock()
        cpm_hub_connector = MagicMock()
        plugin_installer = MagicMock()
        plugin_download = MagicMock()
        plugin = Plugin("cest", "1.0")
        plugin_installer.install.return_value = plugin
        project = Project("Project")
        project_loader.load.return_value = project
        cpm_hub_connector.download_plugin.return_value = plugin_download
        service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

        service.install("cest")

        cpm_hub_connector.download_plugin.assert_called_once_with("cest")
        plugin_installer.install.assert_called_once_with(plugin_download)
        project_loader.add_plugin.assert_called_once_with(plugin)
