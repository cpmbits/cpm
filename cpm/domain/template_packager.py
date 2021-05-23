from cpm.infrastructure import filesystem
from cpm.domain.constants import PROJECT_DESCRIPTOR_FILE


class TemplatePackager(object):
    def pack(self, project_descriptor, build_directory):
        if filesystem.directory_exists(build_directory):
            raise FailedToPackageTemplate(cause='build directory exists')

        filesystem.create_directory(build_directory)
        filesystem.copy_file(PROJECT_DESCRIPTOR_FILE, f'{build_directory}/project.yaml')
        self.__copy_packages(build_directory, project_descriptor)
        self.__copy_mains(build_directory, project_descriptor)
        self.__copy_dockerfiles(build_directory, project_descriptor)
        filesystem.zip(build_directory, f'{project_descriptor.name}')
        filesystem.remove_directory(build_directory)

        return f'{project_descriptor.name}.zip'

    def __copy_dockerfiles(self, build_directory, project_descriptor):
        for target, description in project_descriptor.targets.items():
            if description.dockerfile and filesystem.file_exists(description.dockerfile):
                filesystem.copy_file(description.dockerfile, f'{build_directory}/')

    def __copy_mains(self, build_directory, project_descriptor):
        for target, description in project_descriptor.targets.items():
            relative_path_from_root = filesystem.path_to(description.main)
            if relative_path_from_root:
                filesystem.create_directory(f'{build_directory}/{relative_path_from_root}')
            filesystem.copy_file(description.main, f'{build_directory}/{relative_path_from_root}')

    def __copy_packages(self, build_directory, project_descriptor):
        for package in project_descriptor.build_packages():
            filesystem.copy_directory(package.path, f'{build_directory}/{package.path}')
        for package in project_descriptor.test.packages:
            filesystem.copy_directory(package.path, f'{build_directory}/{package.path}')


class FailedToPackageTemplate(RuntimeError):
    def __init__(self, cause='packaging failure'):
        self.cause = cause
