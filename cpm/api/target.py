from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.project_loader import NotAChromosProject


def add_target(target_service, target_name):
    try:
        target_service.add_target(target_name)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Target {target_name} added to project')
