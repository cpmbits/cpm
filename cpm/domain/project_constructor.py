class ProjectConstructor:
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def exists(self, project_name):
        return self.filesystem.directory_exists(project_name)

    def create(self, project_name):
        self.filesystem.create_directory(project_name)
        self.filesystem.create_file(
            f'{project_name}/project.yaml',
            f'project_name: {project_name}\n'
        )
