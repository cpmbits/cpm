from cpm.domain.project import ROOT_FILE
from cpm.domain.project import Project
from cpm.domain.project import Target


class ProjectLoader(object):
    def __init__(self, yaml_handler):
        self.yaml_handler = yaml_handler

    def load(self):
        try:
            description = self.yaml_handler.load(ROOT_FILE)
            project = Project(description['project_name'])
            self.__parse_targets(description, project)
            return project
        except FileNotFoundError:
            raise NotAChromosProject()

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
        self.yaml_handler.dump(ROOT_FILE, project_description)

    def __as_dict(self, targets):
        return {target: {} for target in targets}


class NotAChromosProject(RuntimeError):
    pass
