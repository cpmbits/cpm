from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.project_commands import ProjectCommands
from cpm.domain.project.project_descriptor_parser import NotACpmProject
from cpm.domain.project.project_loader import ProjectLoader
from cpm.domain.compilation_service import CompilationService


def clean_project(compilation_service):
    try:
        compilation_service.clean()
    except NotACpmProject:
        return Result(FAIL, f'error: not a cpm project')

    return Result(OK, f'clean finished')


def execute(argv):
    project_loader = ProjectLoader()
    cmakelists_builder = CMakeListsBuilder()
    project_builder = ProjectCommands()
    service = CompilationService(project_loader, cmakelists_builder, project_builder)

    result = clean_project(service)

    return result
