from cpm.domain.plugin_loader import PluginLoader
from cpm.domain.project import PROJECT_ROOT_FILE
from cpm.domain.project import Package
from cpm.domain.project import Project
from cpm.domain.project import Target


class ProjectLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler
        self.plugin_loader = PluginLoader(yaml_handler, filesystem)

    def load(self):
        try:
            description = self.yaml_handler.load(PROJECT_ROOT_FILE)
            project = Project(description['project_name'])
            project.add_sources(['main.cpp'])
            for package in self.project_packages(description):
                project.add_package(package)
                project.add_include_directory(self.filesystem.parent_directory(package.path))
                project.add_sources(package.sources)
            project.add_tests(self.test_suites())
            for target in self.described_targets(description):
                project.add_target(target)
            for plugin in self.load_plugins(description):
                project.add_plugin(plugin)
                project.add_sources(plugin.sources)
                for directory in plugin.include_directories:
                    project.add_include_directory(directory)
            return project
        except FileNotFoundError:
            raise NotAChromosProject()

    def described_targets(self, description):
        if 'targets' in description:
            for target in description['targets']:
                yield Target(target, description['targets'][target])
        return []

    def load_plugins(self, description):
        if 'plugins' in description:
            for plugin in description['plugins']:
                yield self.plugin_loader.load(plugin, description['plugins'][plugin])
        return []

    def project_packages(self, description):
        for package in description.get('packages', []):
            yield self.load_package(package, description['packages'][package])
        return []

    def load_package(self, package, package_description):
        cflags = package_description.get('cflags', []) if package_description is not None else []
        sources = self.all_sources(package)
        return Package(f'{package}', sources=sources, cflags=cflags)

    def test_suites(self):
        return self.filesystem.find('tests', 'test_*.cpp')

    def all_sources(self, path):
        return self.filesystem.find(path, '*.cpp') + self.filesystem.find(path, '*.c')

    def save(self, project):
        project_description = {
            'project_name': project.name
        }
        if project.targets:
            project_description['targets'] = {target: {} for target in project.targets}
        if project.plugins:
            project_description['plugins'] = {
                plugin.name: plugin.version for plugin in project.plugins
            }
        self.yaml_handler.dump(PROJECT_ROOT_FILE, project_description)


class NotAChromosProject(RuntimeError):
    pass
