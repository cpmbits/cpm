from cpm.domain.project import PROJECT_ROOT_FILE


class PluginPackager(object):
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def pack(self, project, build_directory):
        if not project.packages:
            raise PackagingFailure(cause='project contains no packages')

        if self.filesystem.directory_exists(build_directory):
            raise PackagingFailure(cause='build directory exists')

        self.filesystem.create_directory(build_directory)
        self.filesystem.copy_file(PROJECT_ROOT_FILE, f'{build_directory}/plugin.yaml')
        for package in project.packages:
            self.filesystem.copy_directory(package.path, f'{build_directory}/{package.path}')
        self.filesystem.zip(build_directory, f'{project.name}')
        self.filesystem.remove_directory(build_directory)

        return f'{project.name}.zip'


class PackagingFailure(RuntimeError):
    def __init__(self, cause='packaging failure'):
        self.cause = cause
