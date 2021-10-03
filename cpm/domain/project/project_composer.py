from cpm.domain.constants import DEFAULT_TARGET
from cpm.infrastructure import filesystem
from cpm.domain.project.project_descriptor import TargetDescription
from cpm.domain.project.project import Project, Target, Package, TestSuite


def compose(project_descriptor, target_name):
    if target_name not in project_descriptor.targets:
        raise TargetNotDescribed()
    project = Project(
        project_descriptor.name,
        version=project_descriptor.version,
        description=project_descriptor.description,
        descriptor=project_descriptor
    )
    project.target = compose_target(target_name, project_descriptor)
    compose_tests(target_name, project_descriptor, project)
    return project


def compose_target(target_name, project_descriptor):
    target = Target(target_name)
    target_description = project_descriptor.targets.get(target_name, TargetDescription(target_name))
    target.cflags = project_descriptor.build.cflags + target_description.build.cflags
    target.cppflags = project_descriptor.build.cppflags + target_description.build.cppflags
    target.ldflags = project_descriptor.build.ldflags + target_description.build.ldflags
    target.libraries = project_descriptor.build.libraries + target_description.build.libraries
    target.include_directories.update(project_descriptor.build.includes)
    target.include_directories.update(project_descriptor.targets[target_name].build.includes)
    target.main = target_description.main
    target.image = target_description.image
    target.dockerfile = target_description.dockerfile
    target.test_image = target_description.test_image
    target.test_dockerfile = target_description.test_dockerfile
    target.toolchain_prefix = target_description.toolchain_prefix
    target.post_build = target_description.post_build
    compose_packages(project_descriptor.build.packages, target)
    compose_packages(target_description.build.packages, target)
    for bit_description in project_descriptor.build.bits.values():
        compose_bit(bit_description, target)
    for bit_description in target_description.build.bits.values():
        compose_bit(bit_description, target)
    return target


def compose_tests(target_name, project_descriptor, project):
    target_description = project_descriptor.targets.get(target_name, TargetDescription(target_name))
    project.test.cflags = project_descriptor.test.cflags + target_description.test.cflags
    project.test.cppflags = project_descriptor.test.cppflags + target_description.test.cppflags
    project.test.ldflags = project_descriptor.test.ldflags + target_description.test.ldflags
    project.test.libraries = project_descriptor.test.libraries + target_description.test.libraries
    project.test.include_directories.update(project_descriptor.test.includes)
    project.test.include_directories.update(target_description.test.includes)
    compose_packages(project_descriptor.test.packages, project.test)
    compose_packages(target_description.test.packages, project.test)

    for bit_description in project_descriptor.test.bits.values():
        compose_bit(bit_description, project.test)

    for test_file in filesystem.find('tests', 'test_*.cpp'):
        name = test_file.split('/')[-1].split('.')[0]
        test_suite = TestSuite(name, test_file)
        project.test.test_suites.append(test_suite)


def compose_packages(packages, target):
    for package_description in packages:
        package = Package(package_description.path)
        package.sources = filesystem.find(package.path, '*.cpp') + filesystem.find(package.path, '*.c')
        package.cflags = package_description.cflags + target.cflags
        package.cppflags = package_description.cppflags + target.cppflags
        target.packages.append(package)
        target.include_directories.add(package_include_directory(package_description))
        package.include_directories = target.include_directories


def compose_bit(bit_description, target):
    adjust_bit_packages_base_path(bit_description, bit_description.build.packages)
    add_packages_to_target_includes(bit_description.build.packages, target)
    bit_target_name = get_bit_target_name(bit_description)
    adjust_bit_packages_base_path(bit_description, bit_description.targets[bit_target_name].build.packages)
    add_packages_to_target_includes(bit_description.targets[bit_target_name].build.packages, target)
    bit_target = compose_target(bit_target_name, bit_description)
    target.bits.append(bit_target)
    add_cflags_to_bit_packages(bit_target, bit_description.declared_bit.cflags)
    add_cppflags_to_bit_packages(bit_target, bit_description.declared_bit.cppflags)


def get_bit_target_name(bit_description):
    if bit_description.declared_bit.target in bit_description.targets:
        return bit_description.declared_bit.target
    else:
        return DEFAULT_TARGET


def adjust_bit_packages_base_path(bit_description, packages):
    for package_description in packages:
        package_description.path = f'bits/{bit_description.name}/{package_description.path}'


def add_packages_to_target_includes(packages, target):
    for package_description in packages:
        target.include_directories.add(package_include_directory(package_description))


def package_include_directory(package_description):
    return filesystem.parent_directory(package_description.path)


def add_cflags_to_bit_packages(bit_target, cflags):
    for package in bit_target.packages:
        package.cflags.extend(cflags)


def add_cppflags_to_bit_packages(bit_target, cppflags):
    for package in bit_target.packages:
        package.cppflags.extend(cppflags)


class TargetNotDescribed(RuntimeError):
    pass
