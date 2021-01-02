import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project.project_loader import ProjectLoader


def new_project(creation_service, options=CreationOptions()):
    if creation_service.exists(options.directory):
        return Result(FAIL, f'error: directory {options.directory} already exists')

    creation_service.create(options)
    return Result(OK, f'Created project {options.project_name}')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm create', description='Create a new cpm project', add_help=False)
    create_parser.add_argument('project_name')
    create_parser.add_argument('-s', '--no-sample-code', required=False, action='store_true', default=False)
    args = create_parser.parse_args(argv)

    project_loader = ProjectLoader()
    service = CreationService(project_loader)

    options = CreationOptions(
        generate_sample_code=not args.no_sample_code,
        project_name=args.project_name,
        directory=args.project_name,
        init_from_existing_sources=False,
    )
    result = new_project(service, options)

    return result
