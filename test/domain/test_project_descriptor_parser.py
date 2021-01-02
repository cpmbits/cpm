import unittest

from cpm.domain.project import project_descriptor
from cpm.domain.project import project_descriptor_parser


class TestProjectDescriptorParser(unittest.TestCase):
    def test_parse_project_descriptor_with_just_the_project_information(self):
        yaml_contents = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'build': {
                'packages': None,
                'bits': None,
                'cflags': None
            },
            'test': None,
            'targets': None
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project == project_descriptor.ProjectDescriptor(
            name='bender bender rodriguez',
            version='1.0',
            description='kill all humans',
            targets={'default': project_descriptor.TargetDescription('default')})

    def test_parse_project_descriptor_with_build_compilation_plan(self):
        yaml_contents = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'build': {
                'packages': {
                    'cpmhub/bits': {
                        'cflags': ['-DHOLA']
                    },
                    'cpmhub/http': None
                },
                'bits': {
                    'sqlite3': '3.32.3'
                },
                'cflags': ['-std=c++11'],
                'ldflags': ['-pg'],
                'libraries': ['pthread']
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.build.packages == [
            project_descriptor.PackageDescription('cpmhub/bits', cflags=['-DHOLA']),
            project_descriptor.PackageDescription('cpmhub/http')
        ]
        assert project.build.cflags == ['-std=c++11']
        assert project.build.ldflags == ['-pg']
        assert project.build.libraries == ['pthread']
        assert len(project.build.declared_bits) == 1
        assert project.build.declared_bits[0] == project_descriptor.DeclaredBit('sqlite3', '3.32.3')

    def test_parse_project_descriptor_with_test_compilation_plan(self):
        yaml_contents = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'test': {
                'packages': {
                    'cpmhub/bits': {},
                    'cpmhub/http': {}
                }
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.test.packages == [
            project_descriptor.PackageDescription('cpmhub/bits'),
            project_descriptor.PackageDescription('cpmhub/http')
        ]

    def test_parse_project_descriptor_with_default_target_image(self):
        yaml_contents = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'targets': {
                'default': {
                    'image': 'cpmbits/bender'
                }
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.targets == {
            'default': project_descriptor.TargetDescription('default', image='cpmbits/bender')
        }

    def test_parse_project_descriptor_with_target_build_compilation_plan(self):
        yaml_contents = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'targets': {
                'arduino': {
                    'dockerfile': 'Dockerfile',
                    'build': {
                        'packages': {
                            'arduino': {},
                        }
                    }
                }
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.targets['arduino'].build.packages == [
            project_descriptor.PackageDescription('arduino')
        ]
        assert project.targets['arduino'].dockerfile == 'Dockerfile'

    def test_parse_project_descriptor_with_target_test_compilation_plan(self):
        yaml_contents = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'targets': {
                'arduino': {
                    'image': 'cpmbits/arduino',
                    'test': {
                        'packages': {
                            'arduino': {},
                        }
                    }
                }
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.targets['arduino'].test.packages == [
            project_descriptor.PackageDescription('arduino')
        ]
