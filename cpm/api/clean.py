from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.project_loader import NotAChromosProject


def clean_project(clean_service):
    try:
        clean_service.clean()
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Clean finished')
