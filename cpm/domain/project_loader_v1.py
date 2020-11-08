import os

from cpm.domain.bit_loader import BitLoader
from cpm.domain.project import Project, ProjectAction, CompileRecipe, Package, Target

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
            project.add_build_recipe(self.load_compile_recipe(description))
            project.add_test_recipe(self.load_compile_recipe(description.get('test', {})))
            project.build.add_sources(['main.cpp'])
            for bit in self.load_local_bits():
                project.build.add_bit(bit)
                for directory in bit.include_directories:
                    project.build.add_include_directory(directory)
            project.add_tests(self.test_suites())
            for target in self.described_targets(description):
                project.add_target(target)
            for action in self.project_actions(description):
                project.add_action(action)
            return project
        except FileNotFoundError:
            raise NotAChromosProject()

    def load_compile_recipe(self, description):
        compile_recipe = CompileRecipe()
        compile_recipe.declared_bits = description.get('bits', {})
        for package in self.project_packages(description):
            compile_recipe.add_package(package)
            compile_recipe.add_include_directory(self.filesystem.parent_directory(package.path))
            compile_recipe.add_sources(package.sources)
        for library in self.link_libraries(description):
            compile_recipe.add_library(library)
        compile_recipe.add_compile_flags(self.compile_flags(description))
        return compile_recipe

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
