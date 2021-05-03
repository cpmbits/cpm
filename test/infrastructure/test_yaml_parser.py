import unittest
import yaml
import pathlib

from cpm.infrastructure import yaml_parser

with open(f'{pathlib.Path(__file__).parent.absolute()}/sample.yaml') as stream:
    sample_yaml = stream.read()


class TestYamlParser(unittest.TestCase):
    def test_parsing_empty_string(self):
        yaml_parse = yaml_parser.parse('')

        assert yaml_parse.as_dict() == {}

    def test_parsing_yaml(self):
        document = '''name: project_name
version: "1.0"

build:
  packages:
    package1:
      cflags:
        - flag1
        flag2
    package2:
  cflags:
    - flag2
test:
  cflags: ['flag3', 'flag4']
'''
        yaml_parse = yaml_parser.parse(document)

        assert yaml_parse.as_dict() == {
            'name': 'project_name',
            'version': '1.0',
            'build': {
                'packages': {
                    'package1': {
                        'cflags': ['flag1 flag2']
                    },
                    'package2': None
                },
                'cflags': ['flag2']
            },
            'test': {
                'cflags': ['flag3', 'flag4']
            }
        }

    def test_dumping_parsed_yaml_document(self):
        document = '''name: project_name
version: 1.0
build:
  packages:
    package1:
    package2:
  cflags:
    - flag1
test:
'''
        yaml_document = yaml_parser.parse(document)

        assert yaml_document.dump() == document

    def test_dumping_modified_parsed_yaml_document(self):
        document = '''name: project_name
version: 1.0'''
        modified_document = '''name: new_name
version: 1.0
'''
        yaml_document = yaml_parser.parse(document)
        yaml_document['name'] = 'new_name'

        assert yaml_document.dump() == modified_document

    def test_with_pyyaml(self):
        yaml_document = yaml_parser.parse(sample_yaml)
        assert yaml_document.as_dict() == yaml.safe_load(sample_yaml)
