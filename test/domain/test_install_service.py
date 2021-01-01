import unittest

from mock import MagicMock
from mock import call

from cpm.domain.install_service import InstallService
from cpm.domain.install_service import BitNotFound
from cpm.domain.bit import Bit
from cpm.domain.project import Project
from cpm.domain.project.project_descriptor import ProjectDescriptor
from cpm.domain.project_loader import NotACpmProject
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure


class TestInstallService(unittest.TestCase):
    def test_install_service_creation(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        InstallService(yaml_handler, bit_installer, cpm_hub_connector)

    def test_install_service_fails_when_project_loader_fails_to_load_project(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        yaml_handler.load.side_effect = NotACpmProject
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        self.assertRaises(NotACpmProject, service.install, 'cest', 'latest')

        yaml_handler.load.assert_called_once()

    def test_install_service_fails_when_authentication_fails(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        cpm_hub_connector.download_bit.side_effect = AuthenticationFailure
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        self.assertRaises(AuthenticationFailure, service.install, 'cest', 'latest')

        cpm_hub_connector.download_bit.assert_called_once_with('cest', 'latest')

    def test_install_service_fails_when_bit_is_not_found_in_cpm_hub(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        cpm_hub_connector.download_bit.side_effect = BitNotFound
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        self.assertRaises(BitNotFound, service.install, 'cest', 'latest')

        cpm_hub_connector.download_bit.assert_called_once_with('cest', 'latest')

    def test_install_service_downloads_bit_then_installs_it_and_updates_the_project(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        bit_download = MagicMock()
        bit_installer.install.return_value = Bit('cest')
        project_description = {
            'name': 'cest'
        }
        yaml_handler.load.return_value = project_description
        cpm_hub_connector.download_bit.return_value = bit_download
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        service.install('cest', 'latest')

        cpm_hub_connector.download_bit.assert_called_once_with('cest', 'latest')
        bit_installer.install.assert_called_once_with(bit_download)

    def test_it_installs_given_bit_version(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        bit_download = MagicMock()
        bit_installer.install.return_value = Bit('cest')
        project = Project('Project')
        yaml_handler.load.return_value = project
        cpm_hub_connector.download_bit.return_value = bit_download
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        service.install('cest', '1.0')

        cpm_hub_connector.download_bit.assert_called_once_with('cest', '1.0')
        bit_installer.install.assert_called_once_with(bit_download)

    def test_it_installs_all_bits_declared_in_project(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        bit_download = MagicMock()
        project = Project('Project')
        project.build.declared_bits = {
            'cest': '1.0',
            'fakeit': '1.0',
        }
        yaml_handler.load.return_value = project
        cpm_hub_connector.download_bit.return_value = bit_download
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        service.install_all()

        cpm_hub_connector.download_bit.assert_has_calls([
            call('cest', '1.0'),
            call('fakeit', '1.0'),
        ])

    def test_it_installs_test_bits_declared_in_project(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        bit_download = MagicMock()
        project = Project('Project')
        project.test.declared_bits = {
            'cest': '1.0',
            'fakeit': '1.0',
        }
        yaml_handler.load.return_value = project
        cpm_hub_connector.download_bit.return_value = bit_download
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        service.install_all()

        cpm_hub_connector.download_bit.assert_has_calls([
            call('cest', '1.0'),
            call('fakeit', '1.0'),
        ])

    def test_it_does_not_install_bit_that_is_already_installed(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        project = Project('Project')
        project.build.add_bit(Bit('cest', '1.0'))
        yaml_handler.load.return_value = project
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        service.install('cest', '1.0')

        cpm_hub_connector.download_bit.assert_not_called()

    def test_it_upgrades_bit_that_is_already_installed_to_a_newer_version(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        project = Project('Project')
        project.build.add_bit(Bit('cest', '1.0'))
        yaml_handler.load.return_value = project
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        service.install('cest', '1.1')

        cpm_hub_connector.download_bit.assert_called_once_with('cest', '1.1')

    def test_it_installs_bit_transitive_dependencies(self):
        yaml_handler = MagicMock()
        cpm_hub_connector = MagicMock()
        bit_installer = MagicMock()
        bit_download = MagicMock()
        chromos_bit = Bit('chromos', version='1.0')
        chromos_bit.declared_bits = {'zeromq': '4.3.2'}
        bit_installer.install.side_effect = [chromos_bit, Bit('zeromq', version='4.3.2')]
        project = Project('Project')
        yaml_handler.load.return_value = project
        cpm_hub_connector.download_bit.return_value = bit_download
        service = InstallService(yaml_handler, bit_installer, cpm_hub_connector)

        service.install('chromos', '1.0')

        cpm_hub_connector.download_bit.assert_has_calls([
            call('chromos', '1.0'),
            call('zeromq', '4.3.2'),
        ])
