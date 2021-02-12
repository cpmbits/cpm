import unittest
import mock

from cpm.domain.project import project_composer
from cpm.domain.project import project_descriptor_parser


class TestProjectComposer(unittest.TestCase):
    def test_should_compose_project_from_project_description_without_packages(self):
        yaml_load = {
            'name': 'HalfLife3',
            'version': '1.0',
            'description': 'I want to believe'
        }
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
        project = project_composer.compose(project_description, 'default')
        assert project.name == 'HalfLife3'
        assert project.version == '1.0'
        assert project.description == 'I want to believe'
        assert project.target.name == 'default'
        assert project.target.main == 'main.cpp'

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_build_package(self, filesystem):
        yaml_load = {
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
        }
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
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
    def test_should_compose_project_for_non_described_target(self, filesystem):
        yaml_load = {
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
        }
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
        project = project_composer.compose(project_description, 'non-described-target')
        assert len(project.target.packages) == 1
        assert project.target.packages[0].path == 'shaders'
        assert project.target.packages[0].sources == ['shaders/shader.cpp', 'shaders/water.c']
        assert project.target.packages[0].cflags == ['-DUSE_PORTAL_GUN', '-Wall']
        assert project.target.cflags == ['-Wall']
        assert project.target.ldflags == ['-pg']
        assert project.target.libraries == ['pthread']
        assert project.target.include_directories == {'.', './include'}

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_target_build_package(self, filesystem):
        yaml_load = {
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
                        'libraries': ['pthread']
                    },
                    'post_build': ['./post_build.sh'],
                    'main': 'main.c'
                }
            }
        }
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
        project = project_composer.compose(project_description, 'default')
        assert len(project.target.packages) == 1
        assert project.target.packages[0].path == 'shaders'
        assert project.target.packages[0].sources == ['shaders/shader.cpp', 'shaders/water.c']
        assert project.target.packages[0].cflags == ['-DUSE_PORTAL_GUN', '-Wall']
        assert project.target.cflags == ['-Wall']
        assert project.target.ldflags == ['-pg']
        assert project.target.libraries == ['pthread']
        assert project.target.include_directories == {'.'}
        assert project.target.post_build == ['./post_build.sh']
        assert project.target.main == 'main.c'

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_target_test_package(self, filesystem):
        yaml_load = {
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
        }
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
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
        yaml_load = {
            'name': 'HalfLife3',
        }
        filesystem.find.side_effect = [['tests/test_one.cpp']]
        filesystem.parent_directory.return_value = '.'
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
        project = project_composer.compose(project_description, 'default')
        assert len(project.test.test_suites) == 1
        assert project.test.test_suites[0].name == 'test_one'
        assert project.test.test_suites[0].main == 'tests/test_one.cpp'
