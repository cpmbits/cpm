from cpm.domain.project import PROJECT_ROOT_FILE
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
            project.add_sources(self.project_sources())
            return project
        except FileNotFoundError:
            raise NotAChromosProject()

    def project_sources(self):
        return self.filesystem.find('sources', '*.cpp') + self.filesystem.find('sources', '*.c')

    def __parse_targets(self, description, project):
        if 'targets' in description:
            for target in description['targets']:
                project.add_target(Target(target, description['targets'][target]))

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
