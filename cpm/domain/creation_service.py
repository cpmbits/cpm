from dataclasses import dataclass

from cpm.domain.sample_code import CPP_HELLO_WORLD


@dataclass
class CreationOptions:
    generate_sample_code: bool = False


class CreationService:
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def exists(self, project_name):
        return self.filesystem.directory_exists(project_name)

    def create(self, project_name, options=CreationOptions()):
        self.filesystem.create_directory(project_name)
        self.filesystem.create_file(
            f'{project_name}/project.yaml',
            f'project_name: {project_name}\n'
        )
        if options.generate_sample_code:
            self.filesystem.create_directory(f'{project_name}/sources')
            self.filesystem.create_file(
                f'{project_name}/sources/main.cpp',
                CPP_HELLO_WORLD
            )
