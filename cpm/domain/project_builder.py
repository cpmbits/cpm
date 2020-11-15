import subprocess

BUILD_DIRECTORY = 'build'
CMAKELISTS = 'CMakeLists.txt'
CMAKE_COMMAND = 'cmake'
NINJA_COMMAND = 'ninja'


class ProjectBuilder(object):
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def build(self, project, target_name):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            self.filesystem.create_directory(BUILD_DIRECTORY)
        self.run_compile_command(CMAKE_COMMAND, '-G', 'Ninja', '..')
        self.run_compile_command(NINJA_COMMAND, project.name)

    def clean(self, project):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            return
        subprocess.run(
            ['ninja', 'clean'],
            cwd=BUILD_DIRECTORY
        )
        self.filesystem.delete_file(CMAKELISTS)
        self.filesystem.remove_directory(BUILD_DIRECTORY)

    def run_compile_command(self, *args):
        result = subprocess.run([*args], cwd=BUILD_DIRECTORY)
        if result.returncode != 0:
            raise BuildError()


class BuildError(RuntimeError):
    pass
