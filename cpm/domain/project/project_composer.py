from cpm.infrastructure import filesystem
from cpm.domain.project.project_descriptor import TargetDescription
from cpm.domain.project.project import Project, Target, Package, TestSuite


def compose(project_descriptor, target_name):
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
    target.ldflags = project_descriptor.build.ldflags + target_description.build.ldflags
    target.libraries = project_descriptor.build.libraries + target_description.build.libraries
    target.include_directories.update(project_descriptor.build.includes)
    target.main = target_description.main
    target.image = target_description.image
    target.dockerfile = target_description.dockerfile
    target.post_build = target_description.post_build
    compose_packages(project_descriptor.build.packages, target)
    compose_packages(target_description.build.packages, target)
    for bit_description in project_descriptor.build.bits.values():
        compose_bit(bit_description, target, target_name)
    return target


def compose_tests(target_name, project_descriptor, project):
    target_description = project_descriptor.targets.get(target_name, TargetDescription(target_name))
    project.test.cflags = project_descriptor.test.cflags + target_description.test.cflags
    project.test.ldflags = project_descriptor.test.ldflags + target_description.test.ldflags
    project.test.libraries = project_descriptor.test.libraries + target_description.test.libraries
    project.test.include_directories.update(project_descriptor.test.includes)
    compose_packages(project_descriptor.test.packages, project.test)
    compose_packages(target_description.test.packages, project.test)

    for bit_description in project_descriptor.test.bits.values():
        compose_bit(bit_description, project.test, target_name)

    for test_file in filesystem.find('tests', 'test_*.cpp'):
        name = test_file.split('/')[-1].split('.')[0]
        test_suite = TestSuite(name, test_file)
        project.test.test_suites.append(test_suite)


def compose_packages(packages, target):
    for package_description in packages:
        package = Package(package_description.path)
        package.sources = filesystem.find(package.path, '*.cpp') + filesystem.find(package.path, '*.c')
        package.cflags = package_description.cflags + target.cflags
        target.packages.append(package)
        target.include_directories.add(package_include_directory(package_description))
        package.include_directories = target.include_directories


def compose_bit(bit_description, target, target_name):
    adjust_bit_packages_base_path(bit_description, bit_description.build.packages)
    if target_name in bit_description.targets:
        adjust_bit_packages_base_path(bit_description, bit_description.targets[target_name].build.packages)
    add_packages_to_target_includes(bit_description.build.packages, target)
    target.bits.append(compose_target(target_name, bit_description))


def adjust_bit_packages_base_path(bit_description, packages):
    for package_description in packages:
        package_description.path = f'bits/{bit_description.name}/{package_description.path}'


def add_packages_to_target_includes(packages, target):
    for package_description in packages:
        target.include_directories.add(package_include_directory(package_description))


def package_include_directory(package_description):
    return filesystem.parent_directory(package_description.path)
