import os
import shlex

import docker
import subprocess
import signal
import sys

from cpm.infrastructure import filesystem
from cpm.domain import constants


class ProjectCommands(object):
    def build(self, project):
        if not filesystem.directory_exists(constants.BUILD_DIRECTORY):
            filesystem.create_directory(constants.BUILD_DIRECTORY)
        self.__build(project, [project.name], post_build=self.__post_build(project))

    def clean(self, project):
        if filesystem.directory_exists(constants.BUILD_DIRECTORY):
            self.__run_command(constants.NINJA_COMMAND, 'clean')
            filesystem.remove_directory(constants.BUILD_DIRECTORY)
        _ignore_exception(lambda: filesystem.delete_file(constants.CMAKELISTS))

    def build_tests(self, project, target_name, files_or_dirs):
        if not filesystem.directory_exists(constants.BUILD_DIRECTORY):
            filesystem.create_directory(constants.BUILD_DIRECTORY)
        if not files_or_dirs:
            self.__build(project, ['tests'])
        else:
            tests_to_run = self.tests_from_args(project, target_name, files_or_dirs)
            self.__build(project, [test.name for test in tests_to_run])

    def run_tests(self, project, target_name, files_or_dirs):
        tests_to_run = project.test.test_suites if not files_or_dirs else self.tests_from_args(project, target_name, files_or_dirs)
        test_results = [self.run_test(test.name) for test in tests_to_run]
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

    def __build(self, project, goals, post_build=''):
        if project.target.image:
            self.__build_using_image(project, project.target.image, goals, post_build)
        elif project.target.dockerfile:
            self.__build_using_dockerfile(project, project.target.dockerfile, goals, post_build)
        else:
            self.__build_goal(goals)

    def __build_goal(self, goals):
        if any(result.returncode != 0 for result in [
            self.__run_command(constants.CMAKE_COMMAND, '-G', 'Ninja', '..'),
            self.__run_command(constants.NINJA_COMMAND, *goals)
        ]):
            raise BuildError

    def __run_command(self, *args, cwd=constants.BUILD_DIRECTORY):
        return subprocess.run([*args], cwd=cwd)

    def __build_using_image(self, project, image_name, goals, post_build):
        client = docker.from_env()
        print(f'pulling {image_name}')
        try:
            client.images.pull(image_name)
        except docker.errors.ImageNotFound:
            raise DockerImageNotFound(image_name)
        except docker.errors.NotFound:
            raise DockerImageNotFound(image_name)
        self.__build_inside_container(client, goals, image_name, project, post_build)

    def __build_using_dockerfile(self, project, dockerfile, goal, post_build):
        client = docker.from_env()
        print(f'building image from {dockerfile}')
        image_name = f'{project.name}_cpm_build'
        client.images.build(path=dockerfile, tag=image_name)
        self.__build_inside_container(client, goal, image_name, project, post_build)

    def __build_inside_container(self, client, goals, image_name, project, post_build):
        filesystem.create_file(
            f'{constants.BUILD_DIRECTORY}/build.sh',
            f'{constants.CMAKE_COMMAND} -G Ninja /{project.name} && {constants.NINJA_COMMAND} {" ".join(goals)}\n'
            f'{post_build}'
        )
        container = client.containers.run(
            image_name,
            command=f'bash /{project.name}/build/build.sh',
            working_dir=f'/{project.name}/build',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )
        print(f'building inside {container.short_id}')
        for log in container.logs(stream=True):
            sys.stdout.write(log.decode())
        exit_code = container.wait()
        if exit_code['StatusCode'] != 0:
            raise BuildError
        container.remove()

    def __post_build(self, project):
        return '\n'.join([f'( cd .. && {post_build} )' for post_build in project.target.post_build])

    def tests_from_args(self, project, target_name, files_or_dirs):
        if not files_or_dirs:
            return 'tests'
        tests = []
        for arg in files_or_dirs:
            if filesystem.is_file(arg):
                tests.append(self.test_from_test_file(project, target_name, arg))
            elif filesystem.is_directory(arg):
                tests.extend(self.test_list_from_directory(project, target_name, arg))
        return tests

    def test_list_from_directory(self, project, target_name, directory):
        return [self.test_from_test_file(project, target_name, test_file) for test_file in filesystem.find(directory, 'test_*.cpp')]

    def test_from_test_file(self, project, target_name, test_file):
        return next(test for test in project.test.test_suites if test.main == test_file)


def _ignore_exception(call):
    try:
        call()
    except:
        pass


class TestsFailed(RuntimeError):
    pass


class BuildError(RuntimeError):
    pass


class DockerImageNotFound(RuntimeError):
    def __init__(self, image_name):
        super(DockerImageNotFound, self).__init__()
        self.image_name = image_name
