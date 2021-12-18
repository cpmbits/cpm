import unittest
import mock
import shutil

from cpm.infrastructure.yaml_parser import YamlParser
from cpm.domain.constants import PROJECT_DESCRIPTOR_FILE
from cpm.domain.project import project_composer
from cpm.domain.project import project_descriptor_parser
from cpm.domain.project.project_descriptor import ProjectDescriptor, TargetDescription, CompilationPlan, PackageDescription


class TestProjectComposer(unittest.TestCase):
    def setUp(self):
        self.parser = YamlParser(pure=True)
        shutil.rmtree(PROJECT_DESCRIPTOR_FILE, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(PROJECT_DESCRIPTOR_FILE, ignore_errors=True)

    def test_should_compose_project_from_project_description_without_packages(self):
        self.write_descriptor({
            'name': 'HalfLife3',
            'version': '1.0',
            'description': 'I want to believe'
        })

        project_description = project_descriptor_parser.parse_from('.')
        project = project_composer.compose(project_description, 'default')

        assert project.name == 'HalfLife3'
        assert project.version == '1.0'
        assert project.description == 'I want to believe'
        assert project.target.name == 'default'
        assert project.target.main == 'main.cpp'

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_build_package(self, filesystem):
        self.write_descriptor({
            'name': 'HalfLife3',
            'build': {
                'packages': {
                    'shaders': {
                        'cflags': ['-DUSE_PORTAL_GUN']
                    }
                },
                'cflags': ['-Wall'],
                'ldflags': ['-pg'],
                'libraries': ['pthread'],
                'includes': ['./include']
            }
        })
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'

        project_description = project_descriptor_parser.parse_from('.')
        project = project_composer.compose(project_description, 'default')

        assert len(project.target.packages) == 1
        assert project.target.packages[0].path == 'shaders'
        assert project.target.packages[0].sources == ['shaders/shader.cpp', 'shaders/water.c']
        assert project.target.packages[0].cflags == ['-DUSE_PORTAL_GUN', '-Wall']
        assert project.target.cflags == ['-Wall']
        assert project.target.ldflags == ['-pg']
        assert project.target.libraries == ['pthread']
        assert project.target.include_directories == {'.', './include'}

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_raise_an_error_when_target_is_not_described(self, filesystem):
        self.write_descriptor({
            'name': 'HalfLife3',
            'build': {
                'packages': {
                    'shaders': {
                        'cflags': ['-DUSE_PORTAL_GUN']
                    }
                },
            }
        })

        project_description = project_descriptor_parser.parse_from('.')
        self.assertRaises(project_composer.TargetNotDescribed, project_composer.compose, project_description, 'non-described-target')

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_target_build_package(self, filesystem):
        self.write_descriptor({
            'name': 'HalfLife3',
            'targets': {
                'default': {
                    'build': {
                        'packages': {
                            'shaders': {
                                'cflags': ['-DUSE_PORTAL_GUN']
                            }
                        },
                        'cflags': ['-Wall'],
                        'ldflags': ['-pg'],
                        'libraries': ['pthread'],
                        'includes': ['./include']
                    },
                    'post_build': ['./post_build.sh'],
                    'main': 'main.c',
                    'image': 'cpmbits/docker',
                    'test_image': 'cpmbits/docker_test',
                    'test_dockerfile': 'test.Dockerfile',
                    'toolchain_prefix': 'arm-linux-gnueabi-'
                }
            }
        })
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'

        project_description = project_descriptor_parser.parse_from('.')
        project = project_composer.compose(project_description, 'default')

        assert len(project.target.packages) == 1
        assert project.target.packages[0].path == 'shaders'
        assert project.target.packages[0].sources == ['shaders/shader.cpp', 'shaders/water.c']
        assert project.target.packages[0].cflags == ['-DUSE_PORTAL_GUN', '-Wall']
        assert project.target.cflags == ['-Wall']
        assert project.target.ldflags == ['-pg']
        assert project.target.libraries == ['pthread']
        assert project.target.include_directories == {'.', './include'}
        assert project.target.post_build == ['./post_build.sh']
        assert project.target.main == 'main.c'
        assert project.target.image == 'cpmbits/docker'
        assert project.target.test_image == 'cpmbits/docker_test'
        assert project.target.test_dockerfile == 'test.Dockerfile'
        assert project.target.toolchain_prefix == 'arm-linux-gnueabi-'

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_target_test_package(self, filesystem):
        self.write_descriptor({
            'name': 'HalfLife3',
            'test': {
                'includes': ['./test/include']
            },
            'targets': {
                'default': {
                    'test': {
                        'packages': {
                            'shaders': {
                                'cflags': ['-DUSE_PORTAL_GUN']
                            }
                        },
                        'cflags': ['-Wall'],
                        'ldflags': ['-pg'],
                        'libraries': ['pthread']
                    },
                }
            }
        })
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'

        project_description = project_descriptor_parser.parse_from('.')
        project = project_composer.compose(project_description, 'default')

        assert len(project.test.packages) == 1
        assert project.test.packages[0].path == 'shaders'
        assert project.test.packages[0].sources == ['shaders/shader.cpp', 'shaders/water.c']
        assert project.test.packages[0].cflags == ['-DUSE_PORTAL_GUN', '-Wall']
        assert project.test.cflags == ['-Wall']
        assert project.test.ldflags == ['-pg']
        assert project.test.libraries == ['pthread']
        assert project.test.include_directories == {'.', './test/include'}

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_test(self, filesystem):
        self.write_descriptor({
            'name': 'HalfLife3',
        })
        filesystem.find.side_effect = [['tests/test_one.cpp']]
        filesystem.parent_directory.return_value = '.'

        project_description = project_descriptor_parser.parse_from('.')
        project = project_composer.compose(project_description, 'default')

        assert len(project.test.test_suites) == 1
        assert project.test.test_suites[0].name == 'test_one'
        assert project.test.test_suites[0].main == 'tests/test_one.cpp'

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_compose_from_description_with_customized_bit_compilation(self, filesystem):
        self.write_descriptor({
            'name': 'HalfLife3',
            'build': {
                'bits': {
                    'arduino': {
                        'version': '1.0.0',
                        'target': 'nano33',
                        'cflags': ['-DBIT_FLAG']
                    }
                }
            }
        })
        filesystem.find.side_effect = [['tests/test_one.cpp'], ['nano33/nano33.cpp'], []]
        filesystem.parent_directory.return_value = '.'

        project_description = project_descriptor_parser.parse_from('.')
        arduino_bit = ProjectDescriptor(
            name='arduino',
            version='1.0.0',
            targets={
                'nano33': TargetDescription(
                    name='nano33',
                    build=CompilationPlan(
                        cflags=['-mcpu=atmel'],
                        packages=[PackageDescription(path='nano33')]
                    )
                )
            },
            declared_bit=project_description.build.declared_bits[0]
        )
        project_description.build.bits['arduino'] = arduino_bit
        project = project_composer.compose(project_description, 'default')

        assert project.target.bits[0].packages[0].path == 'bits/arduino/1.0.0/nano33'
        assert project.target.bits[0].packages[0].cflags == ['-mcpu=atmel', '-DBIT_FLAG']

    def write_descriptor(self, data):
        with open(PROJECT_DESCRIPTOR_FILE, 'w') as stream:
            self.parser.dump(data, stream)
