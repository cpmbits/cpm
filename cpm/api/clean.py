from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.project_builder import ProjectBuilder
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.compilation_service import CompilationService
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def clean_project(compilation_service):
    try:
        compilation_service.clean()
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Clean finished')


def execute(argv):
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    cmakelists_builder = CMakeListsBuilder()
    project_builder = ProjectBuilder(filesystem)
    service = CompilationService(project_loader, cmakelists_builder, project_builder)

    result = clean_project(service)

    return result
