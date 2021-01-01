import unittest
import mock

from cpm.api.install import install_bit
from cpm.api.install import install_project_bits
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.install_service import BitNotFound
from cpm.domain.project.project_descriptor_parser import NotACpmProject
from cpm.infrastructure.http_client import HttpConnectionError


class TestApiInstall(unittest.TestCase):
    def test_bit_install_fails_when_current_directory_is_not_a_chromos_project(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = NotACpmProject

        result = install_bit(install_service, 'cest')

        assert result.status_code == FAIL
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_bit_install_fails_when_http_connection_fails(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = HttpConnectionError

        result = install_bit(install_service, 'cest')

        assert result.status_code == FAIL
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_bit_install_fails_when_bit_is_not_found(self):
        install_service = mock.MagicMock()
        install_service.install.side_effect = BitNotFound

        result = install_bit(install_service, 'cest')

        assert result.status_code == FAIL
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_bit_install(self):
        install_service = mock.MagicMock()

        result = install_bit(install_service, 'cest')

        assert result.status_code == OK
        install_service.install.assert_called_once_with('cest', 'latest')

    def test_bit_install_of_specific_version(self):
        install_service = mock.MagicMock()

        result = install_bit(install_service, 'cest', '1.1')

        assert result.status_code == OK
        install_service.install.assert_called_once_with('cest', '1.1')

    def test_bit_install_of_all_bits_in_project(self):
        install_service = mock.MagicMock()

        result = install_project_bits(install_service)

        assert result.status_code == OK
        install_service.install_all.assert_called_once()

    def test_bit_install_of_all_bits_in_project_fails_when_current_directory_is_not_a_chromos_project(self):
        install_service = mock.MagicMock()
        install_service.install_all.side_effect = NotACpmProject

        result = install_project_bits(install_service)

        assert result.status_code == FAIL

    def test_bit_install_of_all_bits_in_project_fails_when_http_connection_fails(self):
        install_service = mock.MagicMock()
        install_service.install_all.side_effect = HttpConnectionError

        result = install_project_bits(install_service)

        assert result.status_code == FAIL

    def test_bit_install_of_all_bits_in_project_fails_when_one_bit_does_not_exist(self):
        install_service = mock.MagicMock()
        install_service.install_all.side_effect = BitNotFound

        result = install_project_bits(install_service)

        assert result.status_code == FAIL


