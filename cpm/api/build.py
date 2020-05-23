from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.compilation_service import CompilationService
from cpm.domain.cmake_recipe import CMakeRecipe, CompilationError
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def build_project(compilation_service, recipe, target='host'):
    try:
        compilation_service.build(recipe)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')
    except CompilationError:
        return Result(FAIL, f'error: compilation failed')

    return Result(OK, f'Build finished')


def execute(argv):
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = CompilationService(loader)
    recipe = CMakeRecipe(filesystem)

    result = build_project(service, recipe)

    return result

