import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.bit_packager import BitPackager
from cpm.domain.publish_service import PublishService
from cpm.domain.bit_packager import PackagingFailure
from cpm.domain.project.project_descriptor_parser import NotACpmProject
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.cpm_hub_connector_v1 import InvalidCpmHubUrl
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure
from cpm.infrastructure.cpm_hub_connector_v1 import PublicationFailure
from cpm.infrastructure.http_client import HttpConnectionError


def publish_project(publish_service):
    try:
        publish_service.publish()
    except NotACpmProject:
        return Result(FAIL, f'error: not a CPM project')
    except PackagingFailure as error:
        return Result(FAIL, f'error: {error.cause}')
    except HttpConnectionError:
        return Result(FAIL, f'error: failed to connect to CPM Hub')
    except InvalidCpmHubUrl:
        return Result(FAIL, f'error: invalid CPM Hub URL')
    except AuthenticationFailure:
        return Result(FAIL, f'error: invalid credentials')
    except PublicationFailure as error:
        return Result(FAIL, f'error: {error}')
    except KeyboardInterrupt:
        return Result(FAIL, f'interrupted')

    return Result(OK, f'Project published')


def execute(argv):
    publish_parser = argparse.ArgumentParser(prog='cpm publish', description='cpm Package Manager', add_help=False)
    publish_parser.add_argument('-s', '--repository-url', required=True, action='store', default='https://repo.cpmbits.com:8000')
    publish_parser.add_argument('-d', '--dry-run', required=False, action='store_true', default=False)
    args = publish_parser.parse_args(argv)

    packager = BitPackager()
    cpm_hub_connector = CpmHubConnectorV1(repository_url=args.repository_url, dry_run=args.dry_run)
    service = PublishService(packager, cpm_hub_connector)

    result = publish_project(service)

    return result
