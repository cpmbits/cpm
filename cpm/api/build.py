from cpm.argument_parser import ArgumentParser
from cpm.api.result import Result, OK, FAIL
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.compilation_service import CompilationService
from cpm.domain.project_commands import DockerImageNotFound
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound
from cpm.domain.project.project_loader import ProjectLoader, InvalidTarget
from cpm.domain.project_commands import ProjectCommands, BuildError
from cpm.api import install


def build_project(compilation_service, target='default'):
    try:
        print(f'cpm: building target {target}')
        compilation_service.build(target)
    except ProjectDescriptorNotFound:
        return Result(FAIL, f'error: not a cpm project')
    except BuildError:
        return Result(FAIL, f'error: compilation failed')
    except InvalidTarget:
        return Result(FAIL, f'error: unknown target {target}')
    except DockerImageNotFound as e:
        return Result(FAIL, f'error: docker image {e.image_name} not found for target {target}')

    return Result(OK, f'Build finished')


def execute(argv):
    install.execute([])

    create_parser = argument_parser()
    args = create_parser.parse_args(argv)

    project_loader = ProjectLoader()
    cmakelists_builder = CMakeListsBuilder()
    project_commands = ProjectCommands()
    service = CompilationService(project_loader, cmakelists_builder, project_commands)

    result = build_project(service, args.target)

    return result


def argument_parser():
    create_parser = ArgumentParser(prog='cpm build', description=description())
    create_parser.add_argument('target',
                               help='target to build',
                               nargs='?',
                               default='default')
    return create_parser


def print_help():
    return argument_parser().print_help()


def description():
    return 'build the project for the given target (use \'default\' if none is given)'
