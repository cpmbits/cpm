import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.install_service import PluginNotFound, InstallService
from cpm.domain.plugin_installer import PluginInstaller
from cpm.domain.plugin_loader import PluginLoader
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.http_client import HttpConnectionError
from cpm.infrastructure.yaml_handler import YamlHandler


def install_plugin(install_service, plugin):
    try:
        install_service.install(plugin)
    except NotAChromosProject:
        return Result(FAIL, 'error: not a Chromos project')
    except PluginNotFound:
        return Result(FAIL, f'error: plugin {plugin} not found in CPM Hub')
    except HttpConnectionError:
        return Result(FAIL, f'error: failed to connect to CPM Hub')

    return Result(OK, f'Installed plugin "{plugin}"')


def execute(argv):
    create_parser = argparse.ArgumentParser(prog='cpm install', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('plugin_name')
    args = create_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    project_loader = ProjectLoader(yaml_handler, filesystem)
    plugin_loader = PluginLoader(yaml_handler, filesystem)
    plugin_installer = PluginInstaller(filesystem, plugin_loader)
    cpm_hub_connector = CpmHubConnectorV1(filesystem, repository_url='http://localhost:8000/plugins')
    service = InstallService(project_loader, plugin_installer, cpm_hub_connector)

    result = install_plugin(service, args.plugin_name)

    return result
