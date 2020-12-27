import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.compilation_service import CompilationService
from cpm.domain.project_loader import NotACpmProject
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.project_commands import ProjectCommands
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def prep_project(compilation_service, target='default'):
    try:
        compilation_service.update(target)
    except NotACpmProject:
        return Result(FAIL, f'error: not a cpm project')

    return Result(OK, f'CMakeLists.txt ready')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm prep', description='cpm prep', add_help=False)
    create_parser.add_argument('target', nargs='?', default='default')
    args = create_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    cmakelists_builder = CMakeListsBuilder()
    project_commands = ProjectCommands(filesystem)
    service = CompilationService(project_loader, cmakelists_builder, project_commands)

    result = prep_project(service, args.target)

    return result
