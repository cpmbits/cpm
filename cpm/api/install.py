import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.install_service import BitNotFound, InstallService
from cpm.domain.bit_installer import BitInstaller
from cpm.domain.bit_loader import BitLoader
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.cpm_user_configuration import CpmUserConfiguration
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.http_client import HttpConnectionError
from cpm.infrastructure.yaml_handler import YamlHandler


def install_bit(install_service, name, version='latest'):
    try:
        install_service.install(name, version)
    except NotAChromosProject:
        return Result(FAIL, 'error: not a Chromos project')
    except BitNotFound:
        return Result(FAIL, f'error: bit {name} not found in CPM Hub')
    except HttpConnectionError as error:
        return Result(FAIL, f'error: failed to connect to CPM Hub at {error}')

    return Result(OK, f'Installed bit "{name}"')


def install_project_bits(install_service):
    try:
        install_service.install_project_bits()
    except NotAChromosProject:
        return Result(FAIL, 'error: not a Chromos project')
    except BitNotFound as e:
        return Result(FAIL, f'error: bit {e} not found in CPM Hub')
    except HttpConnectionError as error:
        return Result(FAIL, f'error: failed to connect to CPM Hub at {error}')

    return Result(OK, f'Installed bits')


def execute(argv):
    install_bit_arg_parser = argparse.ArgumentParser(prog='cpm install', description='Chromos Package Manager', add_help=False)
    install_bit_arg_parser.add_argument('bit_name', nargs='?')
    args = install_bit_arg_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    bit_loader = BitLoader(yaml_handler, filesystem)
    bit_installer = BitInstaller(filesystem, bit_loader)
    user_configuration = CpmUserConfiguration(yaml_handler, filesystem)
    user_configuration.load()
    cpm_hub_connector = CpmHubConnectorV1(filesystem, repository_url=f'{user_configuration["cpm_hub_url"]}/bits')
    service = InstallService(project_loader, bit_installer, cpm_hub_connector)

    if not args.bit_name:
        result = install_project_bits(service)
    else:
        result = install_bit(service, args.bit_name)

    return result
