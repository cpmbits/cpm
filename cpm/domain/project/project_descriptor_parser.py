import glob

from cpm.infrastructure import yaml_handler
from cpm.domain import constants
from cpm.domain.project.project_descriptor import ProjectDescriptor, TargetDescription, DeclaredBit, CompilationPlan, PackageDescription


def parse_compilation_plan(plan_description):
    compilation_plan = CompilationPlan()
    for bit_name in get_or_default_to(plan_description, 'bits', {}):
        declared_bit = DeclaredBit(bit_name, plan_description['bits'][bit_name])
        compilation_plan.declared_bits.append(declared_bit)
    for package_path in get_or_default_to(plan_description, 'packages', {}):
        package = PackageDescription(package_path,
                                     cflags=package_cflags(plan_description['packages'][package_path]))
        compilation_plan.packages.append(package)
    compilation_plan.cflags = get_or_default_to(plan_description, 'cflags', [])
    compilation_plan.ldflags = get_or_default_to(plan_description, 'ldflags', [])
    compilation_plan.libraries = get_or_default_to(plan_description, 'libraries', [])
    return compilation_plan


def parse_target(target_name, target_description):
    target = TargetDescription(target_name)
    target.image = target_description.get('image', '')
    target.dockerfile = target_description.get('dockerfile', '')
    target.build = parse_compilation_plan(target_description.get('build', {}))
    target.test = parse_compilation_plan(target_description.get('test', {}))
    return target


def parse_targets(targets_description):
    targets = {
        'default': TargetDescription('default')
    }
    for target_name in targets_description:
        targets[target_name] = parse_target(target_name, targets_description[target_name])
    return targets


def parse_yaml(yaml_contents):
    project_description = ProjectDescriptor(yaml_contents['name'])
    project_description.version = yaml_contents.get('version', '')
    project_description.description = yaml_contents.get('description', '')
    project_description.build = parse_compilation_plan(get_or_default_to(yaml_contents, 'build', {}))
    project_description.test = parse_compilation_plan(get_or_default_to(yaml_contents, 'test', {}))
    project_description.targets = parse_targets(get_or_default_to(yaml_contents, 'targets', {}))
    return project_description


def get_or_default_to(dictionary, key, default):
    return dictionary.get(key, default) or default


def parse_from(project_directory):
    try:
        yaml_contents = yaml_handler.load(project_yaml_file(project_directory))
    except FileNotFoundError:
        raise NotACpmProject
    return parse_yaml(yaml_contents)


def project_yaml_file(project_directory):
    return f'{project_directory}/{constants.PROJECT_DESCRIPTOR_FILE}'


def all_bit_yaml_files(project_descriptor):
    return glob.glob(f'{project_descriptor}/bits/*/*.yaml')


def package_cflags(package_description):
    return package_description.get('cflags', []) if type(package_description) is dict else []


class NotACpmProject(RuntimeError):
    pass
