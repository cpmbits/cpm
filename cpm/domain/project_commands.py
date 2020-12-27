import subprocess
import signal

BUILD_DIRECTORY = 'build'
CMAKELISTS = 'CMakeLists.txt'
CMAKE_COMMAND = 'cmake'
NINJA_COMMAND = 'ninja'


class ProjectCommands(object):
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def build(self, project, target_name):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            self.filesystem.create_directory(BUILD_DIRECTORY)
        self.__run_command(CMAKE_COMMAND, '-G', 'Ninja', '..')
        self.__run_command(NINJA_COMMAND, project.name)

    def clean(self, project):
        if self.filesystem.directory_exists(BUILD_DIRECTORY):
            self.__run_command(NINJA_COMMAND, 'clean')
            self.filesystem.remove_directory(BUILD_DIRECTORY)
        _ignore_exception(lambda: self.filesystem.delete_file(CMAKELISTS))

    def build_tests(self, project, target_name, files_or_dirs):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            self.filesystem.create_directory(BUILD_DIRECTORY)
        self.__run_command(CMAKE_COMMAND, '-G', 'Ninja', '..')
        self.__run_command('ninja', 'tests')

    def run_tests(self, project, target_name, files_or_dirs):
        test_results = [self.run_test(test.name) for test in project.tests]
        if any(result.returncode != 0 for result in test_results):
            raise TestsFailed('tests failed')

    def run_test(self, executable):
        result = subprocess.run(
            [f'./{executable}'],
            cwd=BUILD_DIRECTORY
        )
        if result.returncode < 0:
            print(f'{executable} failed with {result.returncode} ({signal.Signals(-result.returncode).name})')
        return result

    def __run_command(self, *args, cwd=BUILD_DIRECTORY):
        return subprocess.run([*args], cwd=cwd)


def _ignore_exception(call):
    try:
        call()
    except:
        pass


class TestsFailed(RuntimeError):
    pass


class BuildError(RuntimeError):
    pass
