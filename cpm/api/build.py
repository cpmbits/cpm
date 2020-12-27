import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.compilation_service import CompilationService
from cpm.domain.compilation_service import DockerImageNotFound
from cpm.domain.project_loader import NotACpmProject
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.project_commands import ProjectCommands, BuildError
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def build_project(compilation_service, target='default'):
    try:
        compilation_service.build(target)
    except NotACpmProject:
        return Result(FAIL, f'error: not a cpm project')
    except BuildError:
        return Result(FAIL, f'error: compilation failed')
    except DockerImageNotFound as e:
        return Result(FAIL, f'error: docker image {e.image_name} not found for target {target}')

    return Result(OK, f'Build finished')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm build', description='cpm build', add_help=False)
    create_parser.add_argument('target', nargs='?', default='default')
    args = create_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    cmakelists_builder = CMakeListsBuilder()
    project_commands = ProjectCommands(filesystem)
    service = CompilationService(project_loader, cmakelists_builder, project_commands)

    result = build_project(service, args.target)

    return result
