from dataclasses import dataclass

from cpm.domain.project import Project
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.sample_code import CPP_HELLO_WORLD


@dataclass
class CreationOptions:
    name: str = 'MyProject'
    directory: str = '.'
    generate_sample_code: bool = True
    init_from_existing_sources: bool = False


class CreationService:
    def __init__(self, filesystem, project_loader):
        self.filesystem = filesystem
        self.project_loader = project_loader

    def exists(self, directory):
        try:
            self.project_loader.load(directory)
            return True
        except NotAChromosProject:
            return False

    def create(self, project_name, options=CreationOptions()):
        project = Project(project_name)
        self.create_project_directory(project_name)
        self.create_project_descriptor_file(project_name)

        if options.generate_sample_code:
            self.generate_sample_code(project)

        return project

    def generate_sample_code(self, project):
        project.add_sources(['main.cpp'])
        self.filesystem.create_file(
            f'{project.name}/main.cpp',
            CPP_HELLO_WORLD
        )

    def create_project_descriptor_file(self, project_name):
        self.filesystem.create_file(
            f'{project_name}/project.yaml',
            f'name: {project_name}\n'
        )

    def create_project_directory(self, project_name):
        self.filesystem.create_directory(project_name)
