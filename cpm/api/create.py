from cpm.api import result
from cpm.domain.creation_service import CreationOptions


def new_project(project_constructor, project_name, options=CreationOptions()):
    if project_constructor.exists(project_name):
        return result.Result(result.FAIL, f'error: directory {project_name} already exists')

    project_constructor.create(project_name, options)
    return result.Result(result.OK, f'Created project {project_name}')

