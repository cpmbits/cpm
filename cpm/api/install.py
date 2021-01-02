import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.install_service import BitNotFound, InstallService
from cpm.domain.bit_installer import BitInstaller
from cpm.domain.project.project_descriptor_parser import NotACpmProject
from cpm.domain.project.project_loader import ProjectLoader
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.cpm_user_configuration import CpmUserConfiguration
from cpm.infrastructure.http_client import HttpConnectionError


def install_bit(install_service, name, version='latest'):
    try:
        install_service.install(name, version)
    except NotACpmProject:
        return Result(FAIL, 'error: not a cpm project')
    except BitNotFound:
        return Result(FAIL, f'error: bit {name} not found in CPM Hub')
    except HttpConnectionError as error:
        return Result(FAIL, f'error: failed to connect to CPM Hub at {error}')

    return Result(OK, f'installed bit {name}:{version}')


def install_project_bits(install_service):
    try:
        install_service.install_all()
    except NotACpmProject:
        return Result(FAIL, 'error: not a cpm project')
    except BitNotFound as e:
        return Result(FAIL, f'error: bit {e} not found in CPM Hub')
    except HttpConnectionError as error:
        return Result(FAIL, f'error: failed to connect to CPM Hub at {error}')

    return Result(OK, f'installed bits')


def execute(argv):
    install_bit_arg_parser = argparse.ArgumentParser(prog='cpm install', description='cpm Package Manager', add_help=False)
    install_bit_arg_parser.add_argument('-s', '--repository-url', required=False, action='store', default='https://repo.cpmbits.com:8000')
    install_bit_arg_parser.add_argument('bit_name', nargs='?')
    args = install_bit_arg_parser.parse_args(argv)

    project_loader = ProjectLoader()
    bit_installer = BitInstaller(project_loader)
    user_configuration = CpmUserConfiguration()
    user_configuration.load()
    repository_url = args.repository_url if args.repository_url else user_configuration["cpm_hub_url"]
    cpm_hub_connector = CpmHubConnectorV1(repository_url=f'{repository_url}/bits')
    service = InstallService(project_loader, bit_installer, cpm_hub_connector)
    bit_name, bit_version = __bit_to_install(args.bit_name)

    if not args.bit_name:
        result = install_project_bits(service)
    else:
        result = install_bit(service, bit_name, bit_version)

    return result


def __bit_to_install(bit_argument):
    parts = f'{bit_argument}:latest'.split(':')
    return parts[0], parts[1]
