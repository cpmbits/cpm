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
        project = project_composer.compose(project_description)
        assert project.name == 'HalfLife3'
        assert project.version == '1.0'
        assert project.description == 'I want to believe'
        assert len(project.targets) == 1
        assert project.targets['default'].name == 'default'
        assert project.targets['default'].main == 'main.cpp'

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
                'libraries': ['pthread']
            }
        }
        filesystem.find.side_effect = [['shaders/shader.cpp'], ['shaders/water.c'], []]
        filesystem.parent_directory.return_value = '.'
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
        project = project_composer.compose(project_description)
        assert len(project.targets['default'].packages) == 1
        assert project.targets['default'].packages[0].path == 'shaders'
        assert project.targets['default'].packages[0].sources == ['shaders/shader.cpp', 'shaders/water.c']
        assert project.targets['default'].packages[0].cflags == ['-DUSE_PORTAL_GUN']
        assert project.targets['default'].cflags == ['-Wall']
        assert project.targets['default'].ldflags == ['-pg']
        assert project.targets['default'].libraries == ['pthread']
        assert project.targets['default'].include_directories == {'.'}

    @mock.patch('cpm.domain.project.project_composer.filesystem')
    def test_should_compose_project_from_project_description_with_one_test(self, filesystem):
        yaml_load = {
            'name': 'HalfLife3',
        }
        filesystem.find.side_effect = [['tests/test_one.cpp']]
        filesystem.parent_directory.return_value = '.'
        project_description = project_descriptor_parser.parse_yaml(yaml_load)
        project = project_composer.compose(project_description)
        assert len(project.tests) == 1
        assert project.tests[0].name == 'test_one'
        assert project.tests[0].target.name == 'default'
        assert project.tests[0].main == 'tests/test_one.cpp'
