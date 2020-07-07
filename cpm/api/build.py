import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.compilation_service import CompilationService
from cpm.domain.compilation_service import DockerImageNotFound
from cpm.domain.cmake_recipe import CMakeRecipe, CompilationError
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def build_project(compilation_service, recipe, target='host'):
    try:
        if target == 'host':
            compilation_service.build(recipe)
        else:
            compilation_service.build_target(target)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')
    except CompilationError:
        return Result(FAIL, f'error: compilation failed')
    except DockerImageNotFound as e:
        return Result(FAIL, f'error: docker image {e.image_name} not found for target {target}')

    return Result(OK, f'Build finished')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm build', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('target', nargs='?', default='host')
    args = create_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = CompilationService(loader)
    recipe = CMakeRecipe(filesystem)

    result = build_project(service, recipe, args.target)

    return result

