import argparse
import sys

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.infrastructure.filesystem import Filesystem


def new_project(creation_service, project_name, options=CreationOptions()):
    if creation_service.exists(project_name):
        return Result(FAIL, f'error: directory {project_name} already exists')

    creation_service.create(project_name, options)
    return Result(OK, f'Created project {project_name}')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm create', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('project_name')
    create_parser.add_argument('-s', '--no-sample-code', required=False, action='store_true', default=False)
    args = create_parser.parse_args(argv)

    service = CreationService(Filesystem())
    options = CreationOptions(generate_sample_code=not args.no_sample_code)
    result = new_project(service, args.project_name, options)

    return result
