from cpm.domain.project_loader import project_descriptor_parser, project_composer

PROJECT_DESCRIPTOR_FILE = 'project.yaml'


class ProjectLoader(object):
    def __init__(self, yaml_handler, filesystem):
        self.filesystem = filesystem
        self.yaml_handler = yaml_handler

    def load(self, directory):
        yaml_load = self.yaml_handler.load(f'{directory}/{PROJECT_DESCRIPTOR_FILE}')
        project_description = project_descriptor_parser.parse(yaml_load)
        return project_composer.compose(project_description, self.filesystem)


class NotAChromosProject(RuntimeError):
    pass
