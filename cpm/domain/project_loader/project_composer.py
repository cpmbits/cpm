from cpm.domain.project.project import Project, Target, Package, Test


def compose(project_description, filesystem):
    project = Project(project_description.name, version=project_description.version, description=project_description.description)
    compose_target('default', project_description, filesystem, project)
    compose_tests('default', project_description, filesystem, project)
    return project


def compose_target(target_name, project_description, filesystem, project):
    target = Target(target_name)
    project.targets[target_name] = target
    for package_description in project_description.build.packages:
        package = Package(package_description.path)
        package.sources = filesystem.find(package.path, '*.cpp') + filesystem.find(package.path, '*.c')
        target.packages.append(package)
        target.include_directories.append(filesystem.parent_directory(package.path))


def compose_tests(target_name, project_description, filesystem, project):
    for test_file in filesystem.find('tests', 'test_*.cpp'):
        name = test_file.split('/')[-1].split('.')[0]
        target = project.targets[target_name]
        test = Test(name, target, test_file)
        project.tests.append(test)
