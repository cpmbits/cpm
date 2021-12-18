import glob
from pathlib import Path

import semver

from cpm.infrastructure.yaml_parser import YamlParser
from cpm.domain import constants
from cpm.domain.project.project_descriptor import ProjectDescriptor, TargetDescription, DeclaredBit, CompilationPlan, PackageDescription


def parse_from(project_directory):
    try:
        parser = YamlParser(pure=True)
        yaml_document = parser.load_from(Path(project_yaml_file(project_directory)))
    except FileNotFoundError:
        raise ProjectDescriptorNotFound
    project_descriptor = digest_yaml(yaml_document)
    project_descriptor.yaml_document = yaml_document
    project_descriptor.parser = parser
    return project_descriptor


def digest_yaml(yaml_contents):
    project_description = ProjectDescriptor()
    project_description.name = required(yaml_contents, 'name', String)
    project_description.version = optional(yaml_contents, 'version', String, '')
    project_description.description = optional(yaml_contents, 'description', String, '')
    build = optional(yaml_contents, 'build', Mapping, default={})
    project_description.build = parse_compilation_plan(build)
    test = optional(yaml_contents, 'test', Mapping, default={})
    project_description.test = parse_compilation_plan(test)
    project_description.targets = parse_targets(get_or_default_to(yaml_contents, 'targets', {}))
    return project_description


def parse_targets(targets_description):
    targets = {
        'default': TargetDescription('default')
    }
    for target_name in targets_description:
        targets[target_name] = parse_target(target_name, targets_description.get(target_name, {}))
    return targets


def parse_target(target_name, target_description):
    target = TargetDescription(target_name)
    target.image = target_description.get('image', '')
    target.dockerfile = target_description.get('dockerfile', '')
    target.test_image = target_description.get('test_image', '')
    target.test_dockerfile = target_description.get('test_dockerfile', '')
    target.toolchain_prefix = target_description.get('toolchain_prefix', '')
    target.format = target_description.get('format', 'binary')
    target.main = target_description.get('main', '')
    target.post_build = target_description.get('post_build', [])
    target.build = parse_compilation_plan(target_description.get('build', {}))
    target.test = parse_compilation_plan(target_description.get('test', {}))
    return target


def parse_compilation_plan(plan_description):
    compilation_plan = CompilationPlan()
    bits = optional(plan_description, 'bits', Mapping, default={})
    for bit_name in bits:
        bit_description = required(bits, bit_name, BitDescription)
        if isinstance(bit_description, str):
            declared_bit = DeclaredBit(bit_name, bits[bit_name])
        else:
            declared_bit = declared_bit_with_customized_compilation(bit_name, bit_description)
        compilation_plan.declared_bits.append(declared_bit)
    packages = optional(plan_description, 'packages', Mapping, default={})
    for package_path in packages:
        package_description = optional(packages, package_path, Mapping, {})
        package = PackageDescription(
            package_path,
            cflags=optional(package_description, 'cflags', sequence_of(String), []),
            cppflags=optional(package_description, 'cppflags', sequence_of(String), []),
        )
        compilation_plan.packages.append(package)
    compilation_plan.cflags = optional(plan_description, 'cflags', sequence_of(String), [])
    compilation_plan.cppflags = optional(plan_description, 'cppflags', sequence_of(String), [])
    compilation_plan.ldflags = optional(plan_description, 'ldflags', sequence_of(String), [])
    compilation_plan.libraries = optional(plan_description, 'libraries', sequence_of(String), [])
    compilation_plan.includes.update(optional(plan_description, 'includes', sequence_of(String), []))
    return compilation_plan


def declared_bit_with_customized_compilation(bit_name, bit_description):
    return DeclaredBit(
        name=bit_name,
        version=required(bit_description, 'version', String),
        cflags=optional(bit_description, 'cflags', Sequence, []),
        cppflags=optional(bit_description, 'cppflags', Sequence, []),
        target=optional(bit_description, 'target', String, '')
    )


def project_yaml_file(project_directory):
    return f'{project_directory}/{constants.PROJECT_DESCRIPTOR_FILE}'


def all_bit_yaml_files(project_descriptor):
    return glob.glob(f'{project_descriptor}/bits/*/*.yaml')


def package_compilation_flags(package_description, field):
    return get_or_default_to(package_description, field, [])


def get_or_default_to(dictionary, key, default):
    if not dictionary:
        return default
    return dictionary.get(key, default) or default


def required(d, key, typ):
    if key not in d:
        raise MissingRequiredField(key)
    typ.validate(d, key)
    return d[key]


def optional(d, key, typ, default=None):
    if key not in d or not d[key]:
        return default
    typ.validate(d, key)
    return d[key]


class String:
    name = 'string'

    @staticmethod
    def validate(d, key):
        value = d[key]
        if not isinstance(value, str):
            raise ParseError(*_location(d, key), f'{key} must be a string')


class Semver(String):
    name = 'semver'

    @staticmethod
    def validate(d, key):
        String.validate(d, key)
        value = d[key]
        if not semver.VersionInfo.isvalid(value):
            raise ParseError(*_location(d, key), f'{key} must be a valid semver string')


class BitDescription:
    name = 'bit_description'

    @staticmethod
    def validate(d, key):
        value = d[key]
        if not isinstance(value, dict) and not isinstance(value, str):
            raise ParseError(*_location(d, key), f'{key} must be a string or a mapping')


class Mapping:
    name = 'mapping'

    @staticmethod
    def validate(d, key):
        value = d[key]
        if not isinstance(value, dict):
            raise ParseError(*_location(d, key), f'{key} must be a mapping')


class Sequence:
    name = 'sequence'

    @staticmethod
    def validate(d, key):
        sequence = d[key]
        if not isinstance(sequence, list):
            raise ParseError(*_location(d, key), f'{key} must be a sequence')


def sequence_of(typ):
    class SequenceOf(Sequence):
        name = f'sequence_of_{typ.name}'

        @staticmethod
        def validate(d, key):
            try:
                Sequence.validate(d, key)
                sequence = d[key]
                for i in range(len(sequence)):
                    typ.validate(sequence, i)
            except ParseError as parse_error:
                raise ParseError(
                    parse_error.parsing_file,
                    parse_error.line,
                    parse_error.col,
                    f'{key} must be a sequence of {typ.name}')

    return SequenceOf


class ProjectDescriptorNotFound(RuntimeError):
    pass


def _location(d, key):
    return d.parsing_file, d.lc.data[key][0], d.lc.data[key][1]


class ParseError(RuntimeError):
    def __init__(self, parsing_file, line, col, message):
        self.parsing_file = parsing_file
        self.line = line
        self.col = col
        self.message = f'{parsing_file}:{line+1}:{col+1}: {message}'


class MissingRequiredField(ParseError):
    def __init__(self, field):
        self.field = field
        self.message = f'{field} is required'
