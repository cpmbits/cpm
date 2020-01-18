from cpm.api import result
from cpm.domain.project_loader import NotAChromosProject


def add(target_service, target_name):
    try:
        target_service.add_target(target_name)
    except NotAChromosProject:
        return result.Result(result.FAIL, f'error: not a Chromos project')

    return result.Result(result.OK, f'Target {target_name} added to project')
