import unittest
import mock

from cpm.domain.bit_packager import BitPackager
from cpm.domain.bit_packager import PackagingFailure
from cpm.domain.project.project_descriptor import ProjectDescriptor, TargetDescription, PackageDescription


class TestBitPackager(unittest.TestCase):
    def test_packaging_bit_raises_exception_when_no_packages_are_declared(self):
        packager = BitPackager()
        project = ProjectDescriptor('cest')

        self.assertRaises(PackagingFailure, packager.pack, project, 'dist')

    @mock.patch('cpm.domain.bit_packager.filesystem')
    def test_packaging_bit_raises_exception_when_output_directory_exists(self, filesystem):
        filesystem.directory_exists.return_value = True
        packager = BitPackager()
        project = ProjectDescriptor('cest')
        project.build.packages.append(PackageDescription('fakeit'))

        self.assertRaises(PackagingFailure, packager.pack, project, 'dist')

    @mock.patch('cpm.domain.bit_packager.filesystem')
    def test_packaging_creates_output_directory(self, filesystem):
        filesystem.directory_exists.return_value = False
        packager = BitPackager()
        project = ProjectDescriptor('cest')
        project.targets['default'] = TargetDescription('default')
        project.build.packages.append(PackageDescription('api'))
        project.targets['default'].build.packages.append(PackageDescription('domain'))

        packager.pack(project, 'dist')

        filesystem.create_directory.assert_called_once_with('dist')
        filesystem.copy_file.assert_called_once_with('project.yaml', 'dist/project.yaml')
        filesystem.copy_directory.assert_has_calls([
            mock.call('api', 'dist/api'),
            mock.call('domain', 'dist/domain'),
        ])
        filesystem.zip.assert_called_once_with('dist', 'cest')
        filesystem.remove_directory.assert_called_once_with('dist')



