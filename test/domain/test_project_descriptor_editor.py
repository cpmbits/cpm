import unittest

from cpm.domain.project import project_descriptor
from cpm.domain.project import project_descriptor_parser


class TestProjectDescriptorEditor(unittest.TestCase):
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