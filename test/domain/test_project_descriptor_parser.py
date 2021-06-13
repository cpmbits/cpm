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
                        'cflags': ['-DHOLA'],
                        'cppflags': ['-DHOLA_CPP'],
                    },
                    'cpmhub/http': None
                },
                'bits': {
                    'sqlite3': '3.32.3'
                },
                'cflags': ['-std=c99'],
                'cppflags': ['-std=c++11'],
                'ldflags': ['-pg'],
                'libraries': ['pthread'],
                'includes': ['./include']
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.build.packages == [
            project_descriptor.PackageDescription('cpmhub/bits', cflags=['-DHOLA'], cppflags=['-DHOLA_CPP']),
            project_descriptor.PackageDescription('cpmhub/http')
        ]
        assert project.build.cflags == ['-std=c99']
        assert project.build.cppflags == ['-std=c++11']
        assert project.build.ldflags == ['-pg']
        assert project.build.libraries == ['pthread']
        assert project.build.includes == {'./include'}
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
                    'image': 'cpmbits/bender',
                    'main': 'main.c',
                    'test_image': 'cpmbits/bender_test',
                    'test_dockerfile': 'test.Dockerfile',
                    'toolchain_prefix': 'arm-linux-gnueabi-'
                }
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.targets == {
            'default': project_descriptor.TargetDescription(
                'default',
                image='cpmbits/bender',
                main='main.c',
                test_image='cpmbits/bender_test',
                test_dockerfile='test.Dockerfile',
                toolchain_prefix='arm-linux-gnueabi-'
            )
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
                        },
                        'ldflags': ['-Wl,--wrap=malloc']
                    },
                    'post_build': [
                        './scripts/package.sh'
                    ]
                }
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.targets['arduino'].build.packages == [
            project_descriptor.PackageDescription('arduino')
        ]
        assert project.targets['arduino'].build.ldflags == ['-Wl,--wrap=malloc']
        assert project.build_packages() == [
            project_descriptor.PackageDescription('arduino')
        ]
        assert project.targets['arduino'].dockerfile == 'Dockerfile'
        assert project.targets['arduino'].post_build == ['./scripts/package.sh']

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

    def test_parse_project_descriptor_with_customized_bit_compilation(self):
        yaml_contents = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'build': {
                'packages': {
                    'cpmhub/http': None
                },
                'bits': {
                    'sqlite3': {
                        'version': '3.32.3',
                        'cflags': ['-DCUSTOM_BIT_DEFINE'],
                        'target': 'arduinoNano33'
                    }
                }
            }
        }
        project = project_descriptor_parser.parse_yaml(yaml_contents)
        assert project.build.packages == [
            project_descriptor.PackageDescription('cpmhub/http')
        ]
        assert project.build.declared_bits[0] == project_descriptor.DeclaredBit(
            name='sqlite3', version='3.32.3', cflags=['-DCUSTOM_BIT_DEFINE'], target='arduinoNano33'
        )
