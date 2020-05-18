import unittest
from mock import MagicMock

from cpm.domain.bit import Bit
from cpm.domain.bit_download import BitDownload
from cpm.domain.bit_installer import BitInstaller


class TestBitInstaller(unittest.TestCase):
    def test_bit_installation_when_bit_was_not_installed_before(self):
        filesystem = MagicMock()
        bit_loader = MagicMock()
        installer = BitInstaller(filesystem, bit_loader)
        bit_download = BitDownload("cest", "1.0", "Yml0IHBheWxvYWQ=")
        bit_loader.load.return_value = Bit("cest")
        filesystem.directory_exists.return_value = False

        bit = installer.install(bit_download)

        filesystem.create_directory.assert_called_once_with('bits/cest')
        filesystem.unzips.assert_called_once_with(b'bit payload', 'bits/cest')
        assert bit.name == "cest"

    def test_bit_installation_when_bit_was_installed_before(self):
        filesystem = MagicMock()
        bit_loader = MagicMock()
        installer = BitInstaller(filesystem, bit_loader)
        bit_download = BitDownload("cest", "1.0", "Yml0IHBheWxvYWQ=")
        bit_loader.load.return_value = Bit("cest")
        filesystem.directory_exists.return_value = True

        bit = installer.install(bit_download)

        filesystem.remove_directory.assert_called_once_with('bits/cest')
        filesystem.create_directory.assert_called_once_with('bits/cest')
        filesystem.unzips.assert_called_once_with(b'bit payload', 'bits/cest')
        assert bit.name == "cest"
