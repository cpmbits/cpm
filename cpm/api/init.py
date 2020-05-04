import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def init_project(creation_service, options=CreationOptions(init_from_existing_sources=True)):
    if creation_service.exists(options.directory):
        directory_print = 'current directory' if options.directory == '.' else f'directory {options.directory}'
        return Result(FAIL, f'error: {directory_print} already contains a CPM project')

    creation_service.create(options)
    return Result(OK, f'Created project {options.project_name}')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm init', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('project_name')
    args = create_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    service = CreationService(filesystem, project_loader)

    options = CreationOptions(
        init_from_existing_sources=True,
        generate_sample_code=False,
        directory='.',
        project_name=args.project_name
    )
    result = init_project(service, options)

    return result
