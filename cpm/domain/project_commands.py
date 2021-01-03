import os
import docker
import subprocess
import signal
import sys

from cpm.infrastructure import filesystem
from cpm.domain import constants


class ProjectCommands(object):
    def build(self, project, target_name):
        if not filesystem.directory_exists(constants.BUILD_DIRECTORY):
            filesystem.create_directory(constants.BUILD_DIRECTORY)
        self.__build(project, target_name, project.name)

    def clean(self, project):
        if filesystem.directory_exists(constants.BUILD_DIRECTORY):
            self.__run_command(constants.NINJA_COMMAND, 'clean')
            filesystem.remove_directory(constants.BUILD_DIRECTORY)
        _ignore_exception(lambda: filesystem.delete_file(constants.CMAKELISTS))

    def build_tests(self, project, target_name, files_or_dirs):
        if not filesystem.directory_exists(constants.BUILD_DIRECTORY):
            filesystem.create_directory(constants.BUILD_DIRECTORY)
        self.__build(project, target_name, 'tests')

    def __build(self, project, target_name, goal):
        if project.targets[target_name].image:
            self.__build_using_image(project, project.targets[target_name].image, goal)
        elif project.targets[target_name].dockerfile:
            self.__build_using_dockerfile(project, project.targets[target_name].dockerfile, goal)
        else:
            self.__build_goal(goal)

    def __build_goal(self, goal):
        if any(result.returncode != 0 for result in [
            self.__run_command(constants.CMAKE_COMMAND, '-G', 'Ninja', '..'),
            self.__run_command(constants.NINJA_COMMAND, goal)
        ]):
            raise BuildError

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

    def __build_using_image(self, project, image_name, goal):
        client = docker.from_env()
        print(f'pulling {image_name}')
        try:
            client.images.pull(image_name)
        except docker.errors.ImageNotFound:
            raise DockerImageNotFound(image_name)
        except docker.errors.NotFound:
            raise DockerImageNotFound(image_name)
        self.__build_inside_container(client, goal, image_name, project)

    def __build_using_dockerfile(self, project, dockerfile, goal):
        client = docker.from_env()
        print(f'building image from {dockerfile}')
        image_name = f'{project.name}_cpm_build'
        client.images.build(path=dockerfile, tag=image_name)
        self.__build_inside_container(client, goal, image_name, project)

    def __build_inside_container(self, client, goal, image_name, project):
        filesystem.create_file(
            f'{constants.BUILD_DIRECTORY}/build.sh',
            f'{constants.CMAKE_COMMAND} -G Ninja /{project.name} && {constants.NINJA_COMMAND} {goal}'
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
