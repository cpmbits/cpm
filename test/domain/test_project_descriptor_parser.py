import unittest

from cpm.domain.project.project_description import ProjectDescription, TargetDescription, PackageDescription, \
    DeclaredBit
from cpm.domain.project_loader import project_descriptor_parser


class TestProjectDescriptorParser(unittest.TestCase):
    def test_parse_project_descriptor_with_just_the_project_information(self):
        project_description = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans'
        }
        project = project_descriptor_parser.parse(project_description)
        assert project == ProjectDescription(
            name='bender bender rodriguez',
            version='1.0',
            description='kill all humans',
            targets={'default': TargetDescription('default')})

    def test_parse_project_descriptor_with_build_compilation_plan(self):
        project_description = {
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
                'cflags': ['-std=c++11']
            }
        }
        project = project_descriptor_parser.parse(project_description)
        assert project.build.packages == [PackageDescription('cpmhub/bits', cflags=['-DHOLA']), PackageDescription('cpmhub/http')]
        assert project.build.cflags == ['-std=c++11']
        assert len(project.build.declared_bits) == 1
        assert project.build.declared_bits[0] == DeclaredBit('sqlite3', '3.32.3')

    def test_parse_project_descriptor_with_test_compilation_plan(self):
        project_description = {
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
        project = project_descriptor_parser.parse(project_description)
        assert project.test.packages == [PackageDescription('cpmhub/bits'), PackageDescription('cpmhub/http')]

    def test_parse_project_descriptor_with_default_target_image(self):
        project_description = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'targets': {
                'default': {
                    'image': 'cpmbits/bender'
                }
            }
        }
        project = project_descriptor_parser.parse(project_description)
        assert project.targets == {
            'default': TargetDescription('default', image='cpmbits/bender')
        }

    def test_parse_project_descriptor_with_target_build_compilation_plan(self):
        project_description = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'targets': {
                'arduino': {
                    'image': 'cpmbits/arduino',
                    'build': {
                        'packages': {
                            'arduino': {},
                        }
                    }
                }
            }
        }
        project = project_descriptor_parser.parse(project_description)
        assert project.targets['arduino'].build.packages == [PackageDescription('arduino')]

    def test_parse_project_descriptor_with_target_test_compilation_plan(self):
        project_description = {
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
        project = project_descriptor_parser.parse(project_description)
        assert project.targets['arduino'].test.packages == [PackageDescription('arduino')]
