import unittest
from unittest import mock
from pathlib import Path

from cpm.infrastructure.yaml_parser import YamlParser

from cpm.domain.constants import PROJECT_DESCRIPTOR_FILE
from cpm.domain.project import project_descriptor_parser
from cpm.domain.project import project_descriptor_editor


class TestProjectDescriptorEditor(unittest.TestCase):
    @mock.patch('cpm.domain.project.project_descriptor_editor.filesystem')
    def test_parse_project_descriptor_with_just_the_project_information(self, filesystem):
        yaml = YamlParser()
        with open(PROJECT_DESCRIPTOR_FILE, 'w') as stream:
            stream.write(f'''name: 'bender bender rodriguez'
version: '1.0'
description: 'kill all humans'
build:
    packages:
    bits:
test:
targets:
''')
        yaml_document = yaml.load_from(Path(PROJECT_DESCRIPTOR_FILE))
        project_descriptor = project_descriptor_parser.digest_yaml(yaml_document)
        project_descriptor.yaml_document = yaml_document

        project_descriptor_editor.update('.', project_descriptor, {'name': 'pepito', 'version': '1.0.0'})

        filesystem.write_file.assert_called_with(f'./{PROJECT_DESCRIPTOR_FILE}', f'''name: pepito
version: 1.0.0
description: kill all humans
build:
  packages:
  bits:
test:
targets:
''')

