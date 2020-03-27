import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.plugin_packager import PluginPackager
from cpm.domain.publish_service import PublishService
from cpm.domain.plugin_packager import PackagingFailure
from cpm.domain.project_loader import NotAChromosProject
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.http_client import HttpConnectionError
from cpm.infrastructure.yaml_handler import YamlHandler


def publish_project(publish_service):
    try:
        publish_service.publish()
    except NotAChromosProject:
        return Result(FAIL, f'error: not a CPM project')
    except PackagingFailure as error:
        return Result(FAIL, f'error: {error.cause}')
    except HttpConnectionError:
        return Result(FAIL, f'error: failed to connect to CPM Hub')

    return Result(OK, f'Project published')


def execute(argv):
    publish_parser = argparse.ArgumentParser(prog='cpm publish', description='Chromos Package Manager', add_help=False)
    publish_parser.add_argument('-s', '--repository-url', required=True, action='store', default='http://localhost:8000/plugins')
    args = publish_parser.parse_args(argv)

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    packager = PluginPackager(filesystem)
    cpm_hub_connector = CpmHubConnectorV1(filesystem, repository_url=args.repository_url)
    service = PublishService(loader, packager, cpm_hub_connector)

    result = publish_project(service)

    return result
