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
    if creation_service.exists(options):
        return Result(FAIL, f'error: directory {options.directory} already contains a CPM project')

    creation_service.create(options)
    return Result(OK, f'Created project {options.name}')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm init', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('project_name')
    args = create_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    service = CreationService(filesystem, project_loader)
    result = init_project(service, args.project_name)

    return result
