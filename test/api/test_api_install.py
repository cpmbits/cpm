import unittest
import mock

from cpm.api.install import install_plugin
from cpm.api.install import install_project_plugins
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.install_service import PluginNotFound
from cpm.domain.project_loader import NotAChromosProject
from cpm.infrastructure.http_client import HttpConnectionError


class TestApiInstall(unittest.TestCase):
    def test_plugin_install_fails_when_current_directory_is_not_a_chromos_project(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = NotAChromosProject

        result = install_plugin(install_service, 'cest')

        assert result.status_code == FAIL
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_plugin_install_fails_when_http_connection_fails(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = HttpConnectionError

        result = install_plugin(install_service, 'cest')

        assert result.status_code == FAIL
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_plugin_install_fails_when_plugin_is_not_found(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = PluginNotFound

        result = install_plugin(install_service, 'cest')

        assert result.status_code == FAIL
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_plugin_install(self):
        install_service = mock.MagicMock()

        result = install_plugin(install_service, 'cest')

        assert result.status_code == OK
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_plugin_install_of_specific_version(self):
        install_service = mock.MagicMock()

        result = install_plugin(install_service, 'cest', '1.1')

        assert result.status_code == OK
        install_service.install.assert_called_once_with('cest', '1.1')

    def test_plugin_install_of_all_plugins_in_project(self):
        install_service = mock.MagicMock()

        result = install_project_plugins(install_service)

        assert result.status_code == OK
        install_service.install_project_plugins.assert_called_once()

    def test_plugin_install_of_all_plugins_in_project_fails_when_current_directory_is_not_a_chromos_project(self):
        install_service = mock.MagicMock()
        install_service.install_project_plugins.side_effect = NotAChromosProject

        result = install_project_plugins(install_service)

        assert result.status_code == FAIL

    def test_plugin_install_of_all_plugins_in_project_fails_when_http_connection_fails(self):
        install_service = mock.MagicMock()
        install_service.install_project_plugins.side_effect = HttpConnectionError

        result = install_project_plugins(install_service)

        assert result.status_code == FAIL

    def test_plugin_install_of_all_plugins_in_project_fails_when_one_plugin_does_not_exist(self):
        install_service = mock.MagicMock()
        install_service.install_project_plugins.side_effect = PluginNotFound

        result = install_project_plugins(install_service)

        assert result.status_code == FAIL


