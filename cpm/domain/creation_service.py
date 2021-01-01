from dataclasses import dataclass

from cpm.infrastructure import filesystem
from cpm.domain.project import Project
from cpm.domain.project.project_descriptor_parser import NotACpmProject
from cpm.domain.sample_code import CPP_HELLO_WORLD


@dataclass
class CreationOptions:
    project_name: str = 'ProjectName'
    directory: str = '.'
    generate_sample_code: bool = True
    init_from_existing_sources: bool = False


class CreationService:
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def exists(self, directory):
        try:
            self.project_loader.load(directory)
            return True
        except NotACpmProject:
            return False

    def create(self, options):
        project = Project(options.project_name)
        if not options.init_from_existing_sources:
            self.create_project_directory(options.directory)
        self.create_project_descriptor_file(options)

        if options.generate_sample_code:
            self.generate_sample_code(project)

        return project

    def generate_sample_code(self, project):
        project.build.add_sources(['main.cpp'])
        filesystem.create_file(
            f'{project.name}/main.cpp',
            CPP_HELLO_WORLD
        )

    def create_project_descriptor_file(self, options):
        filesystem.create_file(
            f"{options.directory}/project.yaml",
            f"name: '{options.project_name}'\n"
            f"version: {options.project_name}\n"
            f"build:\n"
            f"  packages:\n"
            f"  bits:\n"
            f"test:\n"
        )

    def create_project_directory(self, project_name):
        filesystem.create_directory(project_name)
