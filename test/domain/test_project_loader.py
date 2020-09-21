import unittest
import mock

import os

from cpm.domain.bit import Bit
from cpm.domain.project import Package, ProjectAction
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import PROJECT_DESCRIPTOR_FILE
from cpm.domain.project_loader import ProjectLoader


class TestProjectLoader(unittest.TestCase):
    def test_creating_project_loader(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        ProjectLoader(yaml_handler, filesystem)

    def test_loading_project_raises_exception_when_project_descriptor_does_not_exist(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.side_effect = FileNotFoundError()
        loader = ProjectLoader(yaml_handler, filesystem)

        self.assertRaises(NotAChromosProject, loader.load)

    def test_loading_project(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project'
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        yaml_handler.load.assert_called_once_with(f'./{PROJECT_DESCRIPTOR_FILE}')
        assert loaded_project.name == 'Project'

    def test_loading_project_from_a_different_directory(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project'
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load(directory='Project')

        yaml_handler.load.assert_called_once_with(f'Project/{PROJECT_DESCRIPTOR_FILE}')
        assert loaded_project.name == 'Project'

    def test_loading_project_with_specified_version(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'version': '1.5'
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.version == '1.5'

    def test_loading_project_with_one_declared_bit(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'bits': {
                'cest': '1.0'
            }
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.declared_bits == {
            'cest': '1.0'
        }

    def test_loading_project_with_one_declared_test_bit(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'test_bits': {
                'cest': '1.0'
            }
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.declared_test_bits == {
            'cest': '1.0'
        }

    def test_loading_project_with_one_package(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        filesystem.parent_directory.return_value = '.'
        yaml_handler.load.return_value = {
            'name': 'Project',
            'packages': {'cpm-hub': None},
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert project.name == 'Project'
        assert Package(path='cpm-hub') in project.packages
        assert project.include_directories == ['.']

    def test_loading_project_with_one_package_with_cflags(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        yaml_handler.load.return_value = {
            'name': 'Project',
            'packages': {
                'cpm-hub': {
                    'cflags': ['-std=c++11']
                }
            },
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert Package(path='cpm-hub', cflags=['-std=c++11']) in project.packages

    def test_loading_project_with_with_libraries_link_option(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        yaml_handler.load.return_value = {
            'name': 'Project',
            'link_options': {
                'libraries': ['pthread']
            },
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert 'pthread' in project.link_options.libraries

    def test_loading_project_with_with_global_compile_flags(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        yaml_handler.load.return_value = {
            'name': 'Project',
            'compile_flags': ['-g'],
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert '-g' in project.compile_flags

    def test_loading_project_with_one_target(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'targets': {
                'ubuntu': {},
            }
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert 'ubuntu' in loaded_project.targets

    @mock.patch('cpm.domain.project_loader.BitLoader')
    def test_loading_project_with_one_bit(self, BitLoader):
        filesystem = mock.MagicMock()
        bit_loader = mock.MagicMock()
        BitLoader.return_value = bit_loader
        yaml_handler = mock.MagicMock()
        yaml_handler.load.return_value = {'name': 'Project'}
        loader = ProjectLoader(yaml_handler, filesystem)

        filesystem.list_directories.return_value = ['cest']
        bit = Bit('cest')
        bit.add_include_directory('bits/cest')
        bit_loader.load_from.return_value = bit

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.bits == [Bit('cest')]
        assert loaded_project.include_directories == ['bits/cest']

    def test_loading_package_with_sources(self):
        filesystem = mock.MagicMock()
        filesystem.find.side_effect = [['package/file.cpp'], ['package/file.c']]
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)

        package = loader.load_package('package', {})

        assert package == Package(path='package', sources=['package/file.cpp', 'package/file.c'])
        filesystem.find.assert_has_calls([
            mock.call('package', '*.cpp'),
            mock.call('package', '*.c'),
        ])

    def test_finding_project_test_suites(self):
        filesystem = mock.MagicMock()
        filesystem.find.return_value = ['tests/test_project.cpp']
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)

        tests = loader.test_suites()

        assert tests == ['tests/test_project.cpp']
        filesystem.find.assert_called_once_with('tests', 'test_*.cpp')

    def test_loading_local_bits_when_bits_directory_is_empty(self):
        filesystem = mock.MagicMock()
        yaml_handler = mock.MagicMock()
        loader = ProjectLoader(yaml_handler, filesystem)
        filesystem.list_directories.return_value = []

        bits = loader.load_local_bits()

        assert bits == []
        filesystem.list_directories.assert_called_once_with(f'{os.getcwd()}/bits')

    @mock.patch('cpm.domain.project_loader.BitLoader')
    def test_loading_local_bits_when_bits_directory_contains_one_bit(self, BitLoader):
        filesystem = mock.MagicMock()
        yaml_handler = mock.MagicMock()
        bit_loader = mock.MagicMock()
        BitLoader.return_value = bit_loader
        loader = ProjectLoader(yaml_handler, filesystem)

        filesystem.list_directories.return_value = ['cest']
        bit_loader.load_from.return_value = Bit('cest')

        bits = loader.load_local_bits()

        assert bits == [Bit('cest')]
        filesystem.list_directories.assert_called_once_with(f'{os.getcwd()}/bits')
        bit_loader.load_from.assert_called_once_with('bits/cest')

    @mock.patch('cpm.domain.project_loader.BitLoader')
    def test_loading_local_bits_when_bits_directory_contains_many_bits(self, BitLoader):
        filesystem = mock.MagicMock()
        yaml_handler = mock.MagicMock()
        bit_loader = mock.MagicMock()
        BitLoader.return_value = bit_loader
        loader = ProjectLoader(yaml_handler, filesystem)

        filesystem.list_directories.return_value = ['cest', 'base64']
        bit_loader.load_from.side_effect = [Bit('cest'), Bit('base64')]

        bits = loader.load_local_bits()

        assert bits == [Bit('cest'), Bit('base64')]
        filesystem.list_directories.assert_called_once_with(f'{os.getcwd()}/bits')
        bit_loader.load_from.assert_has_calls([
            mock.call('bits/cest'),
            mock.call('bits/base64')
        ])

    def test_loading_project_with_one_action(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        yaml_handler.load.return_value = {
            'name': 'Project',
            'actions': {
                'deploy': 'sudo make me a sandwich'
            }
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        loaded_project = loader.load()

        assert loaded_project.name == 'Project'
        assert loaded_project.actions == [ProjectAction('deploy', 'sudo make me a sandwich')]

    def test_loading_project_with_one_test_package(self):
        yaml_handler = mock.MagicMock()
        filesystem = mock.MagicMock()
        filesystem.find.return_value = []
        filesystem.parent_directory.return_value = '.'
        yaml_handler.load.return_value = {
            'name': 'Project',
            'test_packages': {'mocks': None},
        }
        loader = ProjectLoader(yaml_handler, filesystem)

        project = loader.load()

        assert project.name == 'Project'
        assert Package(path='mocks') in project.test_packages
        assert project.test_include_directories == ['.']
