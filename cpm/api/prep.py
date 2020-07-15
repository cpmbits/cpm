from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.compilation_service import CompilationService
from cpm.domain.cmake_recipe import CMakeRecipe
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def prep_project(compilation_service, recipe):
    try:
        compilation_service.update(recipe)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Update finished')


def execute(argv):
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    service = CompilationService(project_loader)
    recipe = CMakeRecipe(filesystem)

    result = prep_project(service, recipe)

    return result
