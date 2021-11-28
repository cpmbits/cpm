from cpm.argument_parser import ArgumentParser
from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.compilation_service import CompilationService
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound
from cpm.domain.project.project_loader import ProjectLoader
from cpm.domain.project_commands import ProjectCommands


def prep_project(compilation_service, target='default'):
    try:
        compilation_service.update(target)
    except ProjectDescriptorNotFound:
        return Result(FAIL, f'error: not a cpm project')

    return Result(OK, f'CMakeLists.txt ready')


def execute(argv):
    create_parser = argument_parser()
    args = create_parser.parse_args(argv)

    project_loader = ProjectLoader()
    cmakelists_builder = CMakeListsBuilder()
    project_commands = ProjectCommands()
    service = CompilationService(project_loader, cmakelists_builder, project_commands)

    result = prep_project(service, args.target)

    return result


def argument_parser():
    create_parser = ArgumentParser(prog='cpm prep', description=description())
    create_parser.add_argument('target',
                               nargs='?',
                               help='target to to use when generating the CMakeLists.txt file',
                               default='default')
    return create_parser


def print_help():
    return argument_parser().print_help()


def description():
    return 'generate the CMakeLists.txt file for the given target (use \'default\' if none is given)'
