from dataclasses import dataclass

from cpm.domain.project import Project
from cpm.domain.sample_code import CPP_HELLO_WORLD


@dataclass
class CreationOptions:
    generate_sample_code: bool = True


class CreationService:
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def exists(self, project_name):
        return self.filesystem.directory_exists(project_name)

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
            f'project_name: {project_name}\n'
        )

    def create_project_directory(self, project_name):
        self.filesystem.create_directory(project_name)
