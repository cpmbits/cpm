from cpm.api import result


def new_project(project_constructor, project_name):
    if project_constructor.exists(project_name):
        return result.Result(result.FAIL, f'Directory {project_name} already exists')

    project_constructor.create(project_name)
    return result.Result(result.OK, f'Created project {project_name}')
