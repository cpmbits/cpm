import unittest
from unittest import mock

from ruamel.yaml import YAML

from cpm.domain.constants import PROJECT_DESCRIPTOR_FILE
from cpm.domain.project import project_descriptor_parser
from cpm.domain.project import project_descriptor_editor


class TestProjectDescriptorEditor(unittest.TestCase):
    @mock.patch('cpm.domain.project.project_descriptor_editor.filesystem')
    def test_parse_project_descriptor_with_just_the_project_information(self, filesystem):
        yaml_payload = '''name: 'bender bender rodriguez'
version: '1.0'
description: 'kill all humans'
build:
    packages:
    bits:
    cflags: !include file.yaml
test:
targets:
'''
        yaml = YAML()
        yaml_document = yaml.load(yaml_payload)
        project_descriptor = project_descriptor_parser.parse_yaml(yaml_document)
        project_descriptor.yaml_document = yaml_document

        project_descriptor_editor.update('.', project_descriptor, {'name': 'pepito', 'version': '1.0.0'})

        filesystem.write_file.assert_called_with(f'./{PROJECT_DESCRIPTOR_FILE}', '''name: pepito
version: 1.0.0
description: kill all humans
build:
  packages:
  bits:
  cflags: !include file.yaml
test:
targets:
''')

