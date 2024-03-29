import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project.project_loader import ProjectLoader


def init_project(creation_service, options=CreationOptions(init_from_existing_sources=True)):
    if creation_service.exists(options.directory):
        directory_print = 'current directory' if options.directory == '.' else f'directory {options.directory}'
        return Result(FAIL, f'error: {directory_print} already contains a cpm project')

    creation_service.create(options)
    return Result(OK, f'Created project {options.project_name}')


def execute(argv):
    args = argument_parser().parse_args(argv)

    project_loader = ProjectLoader()
    service = CreationService(project_loader)

    options = CreationOptions(
        init_from_existing_sources=True,
        generate_sample_code=False,
        directory='.',
        project_name=args.project_name
    )
    result = init_project(service, options)

    return result


def argument_parser():
    create_parser = argparse.ArgumentParser(prog='cpm init', description=description())
    create_parser.add_argument('project_name',
                               help='name of the project to create')
    return create_parser


def print_help():
    return argument_parser().print_help()


def description():
    return 'initialize the current directory as a cpm project'
