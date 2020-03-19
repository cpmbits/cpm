from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.cmake_recipe import CMakeRecipe
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.build_service import BuildService
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def clean_project(build_service, recipe):
    try:
        build_service.clean(recipe)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Clean finished')


def execute(argv):
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = BuildService(loader)
    recipe = CMakeRecipe(filesystem)

    result = clean_project(service, recipe)

    return result
