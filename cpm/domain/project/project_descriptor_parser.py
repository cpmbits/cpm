import glob
from pathlib import Path

from ruamel.yaml import YAML
from cpm.domain import constants
from cpm.domain.project.project_descriptor import ProjectDescriptor, TargetDescription, DeclaredBit, CompilationPlan, PackageDescription


def __compose_document(self):
    self.parser.get_event()
    node = self.compose_node(None, None)
    self.parser.get_event()
    return node


def __yaml_include(loader, node):
    y = loader.loader
    yaml = YAML(typ=y.typ, pure=y.pure)
    yaml.composer.anchors = loader.composer.anchors
    return yaml.load(Path(node.value))


def parse_from(project_directory):
    try:
        with open(project_yaml_file(project_directory)) as stream:
            payload = stream.read()
        yaml = YAML(typ='safe', pure=True)
        yaml.Composer.compose_document = __compose_document
        yaml.Constructor.add_constructor("!include", __yaml_include)
        yaml_document = yaml.load(payload)
    except FileNotFoundError:
        raise ProjectDescriptorNotFound
    project_descriptor = parse_yaml(yaml_document)
    project_descriptor.yaml_document = yaml_document
    return project_descriptor


def parse_yaml(yaml_contents):
    project_description = ProjectDescriptor(yaml_contents['name'])
    project_description.version = yaml_contents.get('version', '')
    project_description.description = yaml_contents.get('description', '')
    project_description.build = parse_compilation_plan(get_or_default_to(yaml_contents, 'build', {}))
    project_description.test = parse_compilation_plan(get_or_default_to(yaml_contents, 'test', {}))
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
    for bit_name in get_or_default_to(plan_description, 'bits', {}):
        if isinstance(plan_description['bits'][bit_name], str):
            declared_bit = DeclaredBit(bit_name, plan_description['bits'][bit_name])
        else:
            declared_bit = declared_bit_with_customized_compilation(bit_name, plan_description['bits'][bit_name])
        compilation_plan.declared_bits.append(declared_bit)
    for package_path in get_or_default_to(plan_description, 'packages', {}):
        package = PackageDescription(
            package_path,
            cflags=get_or_default_to(plan_description['packages'][package_path], 'cflags', []),
            cppflags=get_or_default_to(plan_description['packages'][package_path], 'cppflags', [])
        )
        compilation_plan.packages.append(package)
    compilation_plan.cflags = get_or_default_to(plan_description, 'cflags', [])
    compilation_plan.cppflags = get_or_default_to(plan_description, 'cppflags', [])
    compilation_plan.ldflags = get_or_default_to(plan_description, 'ldflags', [])
    compilation_plan.libraries = get_or_default_to(plan_description, 'libraries', [])
    compilation_plan.includes.update(get_or_default_to(plan_description, 'includes', []))
    return compilation_plan


def declared_bit_with_customized_compilation(bit_name, bit_description):
    return DeclaredBit(
        name=bit_name,
        version=bit_description['version'],
        cflags=get_or_default_to(bit_description, 'cflags', []),
        cppflags=get_or_default_to(bit_description, 'cppflags', []),
        target=get_or_default_to(bit_description, 'target', '')
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


class ProjectDescriptorNotFound(RuntimeError):
    pass
