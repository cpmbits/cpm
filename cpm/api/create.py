from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.creation_service import CreationOptions


def new_project(project_constructor, project_name, options=CreationOptions()):
    if project_constructor.exists(project_name):
        return Result(FAIL, f'error: directory {project_name} already exists')

    project_constructor.create(project_name, options)
    return Result(OK, f'Created project {project_name}')

