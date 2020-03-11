from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.clean_service import CleanService
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def clean_project(clean_service):
    try:
        clean_service.clean()
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Clean finished')


def execute(argv):
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = CleanService(filesystem, loader)

    result = clean_project(service)

    return result
