from cpm.domain.project.project import Project, Target, Package, Test


def compose(project_description, filesystem):
    project = Project(project_description.name, version=project_description.version, description=project_description.description)
    project.targets['default'] = compose_target('default', project_description, filesystem)
    compose_tests('default', project_description, filesystem, project)
    return project


def compose_target(target_name, project_description, filesystem):
    target = Target(target_name)
    target.cflags = project_description.build.cflags
    compose_packages(filesystem, project_description.build.packages, target)
    for bit_description in project_description.build.bits.values():
        adjust_bit_packages_base_path(bit_description)
        add_bit_packages_to_target_includes(bit_description, filesystem, target)
        target.bits.append(compose_target(target_name, bit_description, filesystem))
    return target


def add_bit_packages_to_target_includes(bit_description, filesystem, target):
    for package_description in bit_description.build.packages:
        target.include_directories.add(package_path(filesystem, package_description))


def adjust_bit_packages_base_path(bit_description):
    for package_description in bit_description.build.packages:
        package_description.path = f'bits/{bit_description.name}/{package_description.path}'


def compose_packages(filesystem, packages, target):
    for package_description in packages:
        package = Package(package_description.path)
        package.sources = filesystem.find(package.path, '*.cpp') + filesystem.find(package.path, '*.c')
        package.cflags = package_description.cflags
        target.packages.append(package)
        target.include_directories.add(package_path(filesystem, package))


def package_path(filesystem, package):
    return filesystem.parent_directory(package.path)


def compose_tests(target_name, project_description, filesystem, project):
    for test_file in filesystem.find('tests', 'test_*.cpp'):
        name = test_file.split('/')[-1].split('.')[0]
        target = project.targets[target_name]
        test = Test(name, target, test_file)
        project.tests.append(test)
