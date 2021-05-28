import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project.project_loader import ProjectLoader
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1, TemplateNotFound


def new_project(creation_service, options=CreationOptions()):
    try:
        if creation_service.exists(options.directory):
            return Result(FAIL, f'error: directory {options.directory} already exists')
        creation_service.create(options)
    except TemplateNotFound:
        return Result(FAIL, f'error: template {options.template_name}:{options.template_version} not found')
    return Result(OK, f'Created project {options.project_name}')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm create', description='Create a new cpm project', add_help=False)
    create_parser.add_argument('project_name')
    create_parser.add_argument('-s', '--repository-url', required=False, action='store', default='https://repo.cpmbits.com:8000')
    create_parser.add_argument('-t', '--template', required=False, action='store')
    args = create_parser.parse_args(argv)

    project_loader = ProjectLoader()
    cpm_hub_connector = CpmHubConnectorV1(repository_url=args.repository_url)
    service = CreationService(project_loader, cpm_hub_connector=cpm_hub_connector)
    template_name, template_version = __template_to_use(args.template)

    options = CreationOptions(
        project_name=args.project_name,
        directory=args.project_name,
        init_from_existing_sources=False,
        init_from_template=True if args.template else False,
        template_name=template_name,
        template_version=template_version
    )
    result = new_project(service, options)

    return result


def __template_to_use(bit_argument):
    parts = f'{bit_argument}:latest'.split(':')
    return parts[0], parts[1]
