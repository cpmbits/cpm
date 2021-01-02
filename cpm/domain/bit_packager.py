from cpm.infrastructure import filesystem
from cpm.domain.constants import PROJECT_DESCRIPTOR_FILE


class BitPackager(object):
    def pack(self, project_descriptor, build_directory):
        if not project_descriptor.build.packages:
            raise PackagingFailure(cause='project contains no packages')

        if filesystem.directory_exists(build_directory):
            raise PackagingFailure(cause='build directory exists')

        filesystem.create_directory(build_directory)
        filesystem.copy_file(PROJECT_DESCRIPTOR_FILE, f'{build_directory}/project.yaml')
        for package in project_descriptor.build.packages:
            filesystem.copy_directory(package.path, f'{build_directory}/{package.path}')
        filesystem.zip(build_directory, f'{project_descriptor.name}')
        filesystem.remove_directory(build_directory)

        return f'{project_descriptor.name}.zip'


class PackagingFailure(RuntimeError):
    def __init__(self, cause='packaging failure'):
        self.cause = cause
