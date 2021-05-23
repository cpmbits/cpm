import unittest
import mock

from cpm.domain.template_packager import TemplatePackager
from cpm.domain.template_packager import FailedToPackageTemplate
from cpm.domain.project.project_descriptor import ProjectDescriptor, TargetDescription, PackageDescription


class TestTemplatePackager(unittest.TestCase):
    @mock.patch('cpm.domain.template_packager.filesystem')
    def test_packager_raises_exception_when_output_directory_exists(self, filesystem):
        filesystem.directory_exists.return_value = True
        packager = TemplatePackager()
        project = ProjectDescriptor('cest')
        project.build.packages.append(PackageDescription('fakeit'))

        self.assertRaises(FailedToPackageTemplate, packager.pack, project, 'dist')

    @mock.patch('cpm.domain.template_packager.filesystem')
    def test_packager_copies_all_to_output_directory_then_zips(self, filesystem):
        packager = TemplatePackager()
        project = ProjectDescriptor('cest')
        project.targets['default'] = TargetDescription('default')
        project.build.packages.append(PackageDescription('api'))
        project.test.packages.append(PackageDescription('test'))
        project.targets['default'].build.packages.append(PackageDescription('domain'))
        project.targets['default'].dockerfile = 'Dockerfile'
        filesystem.directory_exists.return_value = False
        filesystem.path_to.return_value = ''

        packager.pack(project, 'dist')

        filesystem.create_directory.assert_called_once_with('dist')
        filesystem.copy_file.assert_has_calls([
            mock.call('project.yaml', 'dist/project.yaml'),
            mock.call('main.cpp', 'dist/'),
            mock.call('Dockerfile', 'dist/')
        ])
        filesystem.copy_directory.assert_has_calls([
            mock.call('api', 'dist/api'),
            mock.call('domain', 'dist/domain'),
            mock.call('test', 'dist/test')
        ])
        filesystem.zip.assert_called_once_with('dist', 'cest')
        filesystem.remove_directory.assert_called_once_with('dist')



