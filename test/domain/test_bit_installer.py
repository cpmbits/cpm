import unittest
import mock

from cpm.domain.bit import Bit
from cpm.domain.bit_download import BitDownload
from cpm.domain.bit_installer import BitInstaller


class TestBitInstaller(unittest.TestCase):
    @mock.patch('cpm.domain.bit_installer.filesystem')
    def test_bit_installation_when_bit_was_not_installed_before(self, filesystem):
        project_loader = mock.MagicMock()
        installer = BitInstaller(project_loader)
        bit_download = BitDownload("cest", "1.0", "Yml0IHBheWxvYWQ=")
        project_loader.load.return_value = Bit("cest")
        filesystem.directory_exists.return_value = False

        installer.install(bit_download)

        filesystem.create_directory.assert_called_once_with('bits/cest')
        filesystem.unzips.assert_called_once_with(b'bit payload', 'bits/cest')

    @mock.patch('cpm.domain.bit_installer.filesystem')
    def test_bit_installation_when_bit_was_installed_before(self, filesystem):
        project_loader = mock.MagicMock()
        installer = BitInstaller(project_loader)
        bit_download = BitDownload("cest", "1.0", "Yml0IHBheWxvYWQ=")
        project_loader.load.return_value = Bit("cest")
        filesystem.directory_exists.return_value = True

        installer.install(bit_download)

        filesystem.remove_directory.assert_called_once_with('bits/cest')
        filesystem.create_directory.assert_called_once_with('bits/cest')
        filesystem.unzips.assert_called_once_with(b'bit payload', 'bits/cest')
