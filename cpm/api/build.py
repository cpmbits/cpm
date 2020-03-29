from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.build_service import BuildService
from cpm.domain.cmake_recipe import CMakeRecipe, CompilationError
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def build_project(build_service, recipe):
    try:
        build_service.build(recipe)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')
    except CompilationError:
        return Result(FAIL, f'error: compilation failed')

    return Result(OK, f'Build finished')


def execute(argv):
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = BuildService(loader)
    recipe = CMakeRecipe(filesystem)

    result = build_project(service, recipe)

    return result

