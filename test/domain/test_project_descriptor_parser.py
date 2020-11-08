import unittest

from cpm.domain.project.compilation_plan import Package
from cpm.domain.project.project import Project, Target
from cpm.domain.project_loader import project_descriptor_parser


class TestProjectDescriptorParser(unittest.TestCase):
    def test_parse_project_descriptor_with_just_the_project_information(self):
        project_description = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans'
        }
        project = project_descriptor_parser.parse(project_description)
        assert project == Project(
            name='bender bender rodriguez',
            version='1.0',
            description='kill all humans',
            targets={'default': Target('default')})

    def test_parse_project_descriptor_with_build_compilation_plan(self):
        project_description = {
            'name': 'bender bender rodriguez',
            'version': '1.0',
            'description': 'kill all humans',
            'build': {
                'packages': {
                    'cpmhub/bits': {},
                    'cpmhub/http': {}
                }
            }
        }
        project = project_descriptor_parser.parse(project_description)
        assert project.build.packages == [Package('cpmhub/bits'), Package('cpmhub/http')]

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
        assert project.test.packages == [Package('cpmhub/bits'), Package('cpmhub/http')]

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
            'default': Target('default', image='cpmbits/bender')
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
        assert project.targets['arduino'].build.packages == [Package('arduino')]

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
        assert project.targets['arduino'].test.packages == [Package('arduino')]
