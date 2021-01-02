from cpm.infrastructure import filesystem
from cpm.domain.project.project import Project, Target, Package, Test


def compose(project_descriptor):
    project = Project(
        project_descriptor.name,
        version=project_descriptor.version,
        description=project_descriptor.description,
        descriptor=project_descriptor
    )
    # TODO: pass target as argument
    project.targets['default'] = compose_target('default', project_descriptor)
    compose_tests('default', project_descriptor, project)
    return project


def compose_target(target_name, project_descriptor):
    target = Target(target_name)
    target.cflags = project_descriptor.build.cflags
    target.ldflags = project_descriptor.build.ldflags
    target.libraries = project_descriptor.build.libraries
    target.image = project_descriptor.targets[target_name].image
    target.dockerfile = project_descriptor.targets[target_name].dockerfile
    compose_packages(project_descriptor.build.packages, target)
    for bit_description in project_descriptor.build.bits.values():
        adjust_bit_packages_base_path(bit_description, bit_description.build.packages)
        add_packages_to_target_includes(bit_description.build.packages, target)
        target.bits.append(compose_target(target_name, bit_description))
    return target


def compose_tests(target_name, project_descriptor, project):
    for bit_description in project_descriptor.test.bits.values():
        adjust_bit_packages_base_path(bit_description, bit_description.build.packages)
    for test_file in filesystem.find('tests', 'test_*.cpp'):
        name = test_file.split('/')[-1].split('.')[0]
        target = project.targets[target_name]
        test = Test(name, target, test_file)
        test.cflags = project_descriptor.test.cflags
        test.ldflags = project_descriptor.test.ldflags
        test.libraries = project_descriptor.test.libraries
        compose_packages(project_descriptor.test.packages, test)
        for bit_description in project_descriptor.test.bits.values():
            add_packages_to_target_includes(bit_description.build.packages, test)
            target.bits.append(compose_target(target_name, bit_description))
        project.tests.append(test)


def compose_packages(packages, target):
    for package_description in packages:
        package = Package(package_description.path)
        package.sources = filesystem.find(package.path, '*.cpp') + filesystem.find(package.path, '*.c')
        package.cflags = package_description.cflags
        target.packages.append(package)
        target.include_directories.add(package_path(package))


def package_path(package):
    return filesystem.parent_directory(package.path)


def add_packages_to_target_includes(packages, target):
    for package_description in packages:
        target.include_directories.add(package_path(package_description))


def adjust_bit_packages_base_path(bit_description, packages):
    for package_description in packages:
        package_description.path = f'bits/{bit_description.name}/{package_description.path}'

