import subprocess
import signal

from cpm.infrastructure import filesystem
from cpm.domain import constants


class ProjectCommands(object):
    def build(self, project, target_name):
        if not filesystem.directory_exists(constants.BUILD_DIRECTORY):
            filesystem.create_directory(constants.BUILD_DIRECTORY)
        self.__run_command(constants.CMAKE_COMMAND, '-G', 'Ninja', '..')
        self.__run_command(constants.NINJA_COMMAND, project.name)

    def clean(self, project):
        if filesystem.directory_exists(constants.BUILD_DIRECTORY):
            self.__run_command(constants.NINJA_COMMAND, 'clean')
            filesystem.remove_directory(constants.BUILD_DIRECTORY)
        _ignore_exception(lambda: filesystem.delete_file(constants.CMAKELISTS))

    def build_tests(self, project, target_name, files_or_dirs):
        if not filesystem.directory_exists(constants.BUILD_DIRECTORY):
            filesystem.create_directory(constants.BUILD_DIRECTORY)
        self.__run_command(constants.CMAKE_COMMAND, '-G', 'Ninja', '..')
        self.__run_command('ninja', 'tests')

    def run_tests(self, project, target_name, files_or_dirs):
        test_results = [self.run_test(test.name) for test in project.tests]
        if any(result.returncode != 0 for result in test_results):
            raise TestsFailed('tests failed')

    def run_test(self, executable):
        result = subprocess.run(
            [f'./{executable}'],
            cwd=constants.BUILD_DIRECTORY
        )
        if result.returncode < 0:
            print(f'{executable} failed with {result.returncode} ({signal.Signals(-result.returncode).name})')
        return result

    def __run_command(self, *args, cwd=constants.BUILD_DIRECTORY):
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
