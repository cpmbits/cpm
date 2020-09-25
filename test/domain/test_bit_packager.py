import unittest
from mock import MagicMock, call

from cpm.domain.bit_packager import BitPackager
from cpm.domain.bit_packager import PackagingFailure
from cpm.domain.project import Project, Package


class TestBitPackager(unittest.TestCase):
    def test_packaging_bit_raises_exception_when_no_packages_are_declared(self):
        filesystem = MagicMock()
        packager = BitPackager(filesystem)
        project = Project('cest')

        self.assertRaises(PackagingFailure, packager.pack, project, 'dist')

    def test_packaging_bit_raises_exception_when_output_directory_exists(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = True
        packager = BitPackager(filesystem)
        project = Project('cest')
        project.build.add_package(Package('fakeit'))

        self.assertRaises(PackagingFailure, packager.pack, project, 'dist')

    def test_packaging_creates_output_directory(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        packager = BitPackager(filesystem)
        project = Project('cest')
        project.build.add_package(Package('api'))
        project.build.add_package(Package('domain'))

        packager.pack(project, 'dist')

        filesystem.create_directory.assert_called_once_with('dist')
        filesystem.copy_file.assert_called_once_with('project.yaml', 'dist/bit.yaml')
        filesystem.copy_directory.assert_has_calls([
            call('api', 'dist/api'),
            call('domain', 'dist/domain'),
        ])
        filesystem.zip.assert_called_once_with('dist', 'cest')
        filesystem.remove_directory.assert_called_once_with('dist')



