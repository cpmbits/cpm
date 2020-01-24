from cpm.domain.project import PROJECT_ROOT_FILE, Plugin
from cpm.domain.project import Project
from cpm.domain.project import Target


class ProjectLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler

    def load(self):
        try:
            description = self.yaml_handler.load(PROJECT_ROOT_FILE)
            project = Project(description['project_name'])
            for target in self.described_targets(description):
                project.add_target(target)
            for plugin in self.described_plugins(description):
                project.add_plugin(plugin)
            project.add_sources(self.project_sources() + self.plugin_sources(project.plugins))
            project.add_tests(self.test_suites())
            return project
        except FileNotFoundError:
            raise NotAChromosProject()

    def described_targets(self, description):
        if 'targets' in description:
            for target in description['targets']:
                yield Target(target, description['targets'][target])

    def described_plugins(self, description):
        if 'plugins' in description:
            for plugin in description['plugins']:
                yield Plugin(plugin, description['plugins'][plugin])

    def project_sources(self):
        return self.all_sources('sources')

    def plugin_sources(self, plugins):
        return [source for plugin in plugins for source in self.all_sources(f'plugins/{plugin.name}/sources')]

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
                plugin.name: plugin.properties for plugin in project.plugins
            }
        self.yaml_handler.dump(PROJECT_ROOT_FILE, project_description)


class NotAChromosProject(RuntimeError):
    pass
