from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.project_loader import NotAChromosProject


def build_project(build_service, recipe):
    try:
        build_service.build(recipe)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Build finished')
