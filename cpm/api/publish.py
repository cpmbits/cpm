from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.project_loader import NotAChromosProject


def publish_project(publish_service):
    try:
        publish_service.publish()
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Build finished')
