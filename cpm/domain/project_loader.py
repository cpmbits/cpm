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
            self.__parse_targets(description, project)
            self.__parse_plugins(description, project)
            project.add_sources(self.__find_c_cpp_sources_at('sources'))
            project.add_sources(self.__plugin_sources(project))
            return project
        except FileNotFoundError:
            raise NotAChromosProject()

    def __find_c_cpp_sources_at(self, path):
        return self.filesystem.find(path, '*.cpp') + self.filesystem.find(path, '*.c')

    def __plugin_sources(self, project):
        plugin_sources = []
        for plugin in project.plugins:
            plugin_sources += self.__find_c_cpp_sources_at(f'plugins/{plugin}/sources')
        return plugin_sources

    def __parse_targets(self, description, project):
        if 'targets' in description:
            for target in description['targets']:
                project.add_target(Target(target, description['targets'][target]))

    def __parse_plugins(self, description, project):
        if 'plugins' in description:
            for plugin in description['plugins']:
                project.add_plugin(Plugin(plugin, description['plugins'][plugin]))

    def save(self, project):
        project_description = {
            'project_name': project.name
        }
        if project.targets:
            project_description['targets'] = self.__as_dict(project.targets)
        self.yaml_handler.dump(PROJECT_ROOT_FILE, project_description)

    def __as_dict(self, targets):
        return {target: {} for target in targets}


class NotAChromosProject(RuntimeError):
    pass
