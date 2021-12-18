import unittest
import os
import shutil

from cpm.domain.project import project_descriptor_parser
from cpm.infrastructure import filesystem


class TestSchemaValidation(unittest.TestCase):
    PROJECT_NAME = 'test_project'
    TEST_DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}'
    PROJECT_DIRECTORY = f'{TEST_DIRECTORY}/{PROJECT_NAME}'

    def setUp(self):
        self.cwd = os.getcwd()
        shutil.rmtree(self.PROJECT_DIRECTORY, ignore_errors=True)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.PROJECT_DIRECTORY, ignore_errors=True)

    def test_project_name_is_required(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """pepe: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'name is required'

    def test_project_name_must_be_a_string(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:1:1: name must be a string'

    def test_project_version_must_be_a_string(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:2:1: version must be a string'

    def disabled_test_project_version_must_be_a_valid_semver_value(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "pepin"
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:2:1: version must be a valid semver string'

    def test_build_compilation_plan_must_be_a_mapping(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:3:1: build must be a mapping'

    def test_bits_in_compilation_plan_must_be_a_mapping(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  bits: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:4:3: bits must be a mapping'

    def test_bits_in_compilation_plan_can_be_empty(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  bits:
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

    def test_bits_configuration_in_compilation_plan(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  bits:
    bit_name: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:5:5: bit_name must be a string or a mapping'

    def test_packages_in_compilation_plan_must_be_a_mapping(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  packages: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:4:3: packages must be a mapping'

    def test_package_description_in_compilation_plan_must_be_a_mapping(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  packages:
    package_name: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:5:5: package_name must be a mapping'

    def test_cflags_in_package_description_in_compilation_plan_must_be_a_sequence(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  packages:
    package_name:
      cflags: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:6:7: cflags must be a sequence of string'

    def test_cflags_in_package_description_in_compilation_plan_must_be_a_sequence_of_strings(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  packages:
    package_name:
      cflags: [123, '123']
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:6:16: cflags must be a sequence of string'

    def test_cflags_in_compilation_plan_must_be_a_sequence_of_strings(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  cflags: [123, '123']
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:4:12: cflags must be a sequence of string'

    def test_cppflags_in_compilation_plan_must_be_a_sequence_of_strings(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  cppflags: [123, '123']
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:4:14: cppflags must be a sequence of string'

    def test_ldflags_in_compilation_plan_must_be_a_sequence_of_strings(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  ldflags: [123, '123']
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:4:13: ldflags must be a sequence of string'

    def test_libraries_in_compilation_plan_must_be_a_sequence_of_strings(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  libraries: [123, '123']
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:4:15: libraries must be a sequence of string'

    def test_includes_in_compilation_plan_must_be_a_sequence_of_strings(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
build:
  includes: [123, '123']
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:4:14: includes must be a sequence of string'

    def test_test_compilation_plan_must_be_a_mapping(self):
        os.mkdir(self.PROJECT_DIRECTORY)
        descriptor_contents = """name: test_project
version: "1.0.0"
test: 123
"""
        filesystem.create_file(f'{self.PROJECT_DIRECTORY}/project.yaml', descriptor_contents)
        with self.assertRaises(project_descriptor_parser.ParseError) as context:
            project_descriptor_parser.parse_from(self.PROJECT_DIRECTORY)

        assert str(context.exception.message) == 'project.yaml:3:1: test must be a mapping'
