import os

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
            filesystem.remove_directory(constants.BUILD_DIRECTORY)
        _ignore_exception(lambda: filesystem.delete_file(constants.CMAKELISTS))

    def build_tests(self, project, files_or_dirs):
        if not filesystem.directory_exists(constants.BUILD_DIRECTORY):
            filesystem.create_directory(constants.BUILD_DIRECTORY)
        if not files_or_dirs:
            self.__build_tests(project, ['tests'])
        else:
            tests_to_run = self.tests_from_args(project, files_or_dirs)
            self.__build_tests(project, [test.name for test in tests_to_run])

    def __build_tests(self, project, goals, post_build=''):
        if project.target.test_image and project.target.test_dockerfile:
            print('cpm: warning: both "test_image" and "test_dockerfile" options are specified, will use "test_image"')
        if project.target.test_image:
            self.__build_using_image(
                project,
                project.target.test_image,
                goals,
                post_build
            )
        elif project.target.test_dockerfile:
            self.__build_using_dockerfile(
                project,
                project.target.test_dockerfile,
                self.__test_image_name(project),
                goals,
                post_build
            )
        else:
            self.__build_goal(goals)

    def __build(self, project, goals, post_build=''):
        if project.target.image and project.target.dockerfile:
            print('cpm: warning: both "image" and "dockerfile" options are specified, will use "image"')
        if project.target.image:
            self.__build_using_image(
                project,
                project.target.image,
                goals,
                post_build
            )
        elif project.target.dockerfile:
            self.__build_using_dockerfile(
                project,
                project.target.dockerfile,
                self.__build_image_name(project),
                goals,
                post_build
            )
        else:
            self.__build_goal(goals)

    def __build_goal(self, goals):
        if any(result.returncode != 0 for result in [
            self.__run_command(constants.CMAKE_COMMAND, '-G', 'Ninja', '..'),
            self.__run_command(constants.NINJA_COMMAND, *goals)
        ]):
            raise BuildError

    def __build_using_image(self, project, image_name, goals, post_build):
        print(f'cpm: using Docker image {image_name}')
        client = docker.from_env()
        try:
            client.images.pull(image_name)
        except docker.errors.ImageNotFound:
            raise DockerImageNotFound(image_name)
        except docker.errors.NotFound:
            raise DockerImageNotFound(image_name)
        self.__build_inside_container(client, project, image_name, goals, post_build)

    def __build_using_dockerfile(self, project, dockerfile, image_name, goals, post_build):
        print(f'cpm: building image from {dockerfile}')
        client = docker.from_env()
        with open(dockerfile, 'rb') as fileobj:
            client.images.build(path='.', fileobj=fileobj, tag=image_name)
        self.__build_inside_container(client, project, image_name, goals, post_build)

    def __build_inside_container(self, client, project, image_name, goals, post_build):
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
            environment=[f'PROJECT_NAME={project.name}', f'PROJECT_VERSION={project.version}'],
            detach=True
        )
        print(f'cpm: building inside {container.short_id}')
        for log in container.logs(stream=True):
            sys.stdout.write(log.decode())
        exit_code = container.wait()
        if exit_code['StatusCode'] != 0:
            raise BuildError
        container.remove()

    def __build_image_name(self, project):
        return f'{project.name}_cpm_build'.lower()

    def __test_image_name(self, project):
        return f'{project.name}_cpm_test'

    def run_tests(self, project, files_or_dirs, test_args=()):
        tests_to_run = project.test.test_suites if not files_or_dirs else self.tests_from_args(project, files_or_dirs)
        if project.target.test_image:
            test_results = self.__run_tests_using_image(
                project,
                project.target.test_image,
                tests_to_run,
                test_args
            )
        elif project.target.test_dockerfile:
            test_results = self.__run_tests_using_dockerfile(
                project,
                self.__test_image_name(project),
                tests_to_run,
                test_args
            )
        else:
            test_results = [self.run_test(test.name, test_args) for test in tests_to_run]
        if any(result != 0 for result in test_results):
            raise TestsFailed('tests failed')

    def run_test(self, executable, test_args):
        result = subprocess.run(
            [f'./{constants.BUILD_DIRECTORY}/{executable}'] + test_args
        )
        if result.returncode < 0:
            print(f'cpm: {executable} failed with {result.returncode} ({signal.Signals(-result.returncode).name})')
        return result.returncode

    def __run_tests_using_image(self, project, image_name, tests_to_run, test_args):
        client = docker.from_env()
        try:
            client.images.pull(image_name)
        except docker.errors.ImageNotFound:
            raise DockerImageNotFound(image_name)
        except docker.errors.NotFound:
            raise DockerImageNotFound(image_name)
        return [self.__run_test_inside_container(project, client, image_name, test.name, test_args) for test in tests_to_run]

    def __run_tests_using_dockerfile(self, project, image_name, tests_to_run, test_args):
        client = docker.from_env()
        return [self.__run_test_inside_container(project, client, image_name, test.name, test_args) for test in tests_to_run]

    def __run_test_inside_container(self, project, client, image_name, executable, test_args):
        container = client.containers.run(
            image_name,
            command=f'./{constants.BUILD_DIRECTORY}/{executable} {" ".join(test_args)}',
            working_dir=f'/{project.name}',
            volumes={f'{os.getcwd()}': {'bind': f'/{project.name}', 'mode': 'rw'}},
            user=f'{os.getuid()}:{os.getgid()}',
            detach=True
        )
        for log in container.logs(stream=True):
            sys.stdout.write(log.decode())
        exit_code = container.wait()
        result = exit_code['StatusCode']
        container.remove()
        if result < 0:
            print(f'cpm: {executable} failed with {result} ({signal.Signals(-result).name})')
        return result

    def __run_command(self, *args, cwd=constants.BUILD_DIRECTORY):
        return subprocess.run([*args], cwd=cwd)

    def __post_build(self, project):
        return '\n'.join([f'( cd .. && {post_build} )' for post_build in project.target.post_build])

    def tests_from_args(self, project, files_or_dirs):
        if not files_or_dirs:
            return 'tests'
        tests = []
        for arg in files_or_dirs:
            if filesystem.is_file(arg):
                tests.append(self.test_from_test_file(project, arg))
            elif filesystem.is_directory(arg):
                tests.extend(self.test_list_from_directory(project, arg))
        return tests

    def test_list_from_directory(self, project, directory):
        return [self.test_from_test_file(project, test_file) for test_file in filesystem.find(directory, 'test_*.cpp')]

    def test_from_test_file(self, project, test_file):
        return next(test for test in project.test.test_suites if test.main == test_file)


def _ignore_exception(call):
    try:
        call()
    except:
        pass


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class TestsFailed(RuntimeError):
    pass


class BuildError(RuntimeError):
    pass


class DockerImageNotFound(RuntimeError):
    def __init__(self, image_name):
        super(DockerImageNotFound, self).__init__()
        self.image_name = image_name
