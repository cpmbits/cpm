import os
from cpm.domain.bit_loader import BitLoader
from cpm.domain.project import ProjectAction
from cpm.domain.project import Package
from cpm.domain.project import Project
from cpm.domain.project import Target

PROJECT_DESCRIPTOR_FILE = 'project.yaml'


class ProjectLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler
        self.bit_loader = BitLoader(yaml_handler, filesystem)

    def load(self, directory='.'):
        try:
            description = self.yaml_handler.load(f'{directory}/{PROJECT_DESCRIPTOR_FILE}')
            project = Project(description['name'])
            project.version = description.get('version', "0.1")
            project.add_sources(['main.cpp'])
            project.declared_bits = description.get('bits', {})
            project.declared_test_bits = description.get('test_bits', {})
            for package in self.project_packages(description):
                project.add_package(package)
                project.add_include_directory(self.filesystem.parent_directory(package.path))
                project.add_sources(package.sources)
            for package in self.project_test_packages(description):
                project.add_test_package(package)
                project.add_test_include_directory(self.filesystem.parent_directory(package.path))
                project.add_test_sources(package.sources)
            project.add_tests(self.test_suites())
            for target in self.described_targets(description):
                project.add_target(target)
            for bit in self.load_local_bits():
                project.add_bit(bit)
                for directory in bit.include_directories:
                    project.add_include_directory(directory)
            for library in self.link_libraries(description):
                project.add_library(library)
            project.add_compile_flags(self.compile_flags(description))
            for action in self.project_actions(description):
                project.add_action(action)
            return project
        except FileNotFoundError:
            raise NotAChromosProject()

    def described_targets(self, description):
        if 'targets' in description:
            for target in description['targets']:
                yield Target(target, description['targets'][target])
        return []

    def load_local_bits(self):
        bit_directories = self.filesystem.list_directories(f'{os.getcwd()}/bits')
        return [self.bit_loader.load_from(f'bits/{directory}') for directory in bit_directories]

    def load_bits(self, description):
        if 'bits' in description:
            for bit in description['bits']:
                yield self.bit_loader.load(bit)
        return []

    def project_packages(self, description):
        for package in description.get('packages', []):
            yield self.load_package(package, description['packages'][package])
        return []

    def project_test_packages(self, description):
        for package in description.get('test_packages', []):
            yield self.load_package(package, description['test_packages'][package])
        return []

    def load_package(self, package, package_description):
        cflags = package_description.get('cflags', []) if package_description is not None else []
        sources = self.all_sources(package)
        return Package(f'{package}', sources=sources, cflags=cflags)

    def test_suites(self):
        return self.filesystem.find('tests', 'test_*.cpp')

    def all_sources(self, path):
        return self.filesystem.find(path, '*.cpp') + self.filesystem.find(path, '*.c')

    def link_libraries(self, description):
        link_options = description.get('link_options', {})
        return link_options.get('libraries', [])

    def project_actions(self, description):
        for action in description.get('actions', []):
            yield ProjectAction(action, description['actions'][action])

    def compile_flags(self, description):
        return description.get('compile_flags', [])


class NotAChromosProject(RuntimeError):
    pass
