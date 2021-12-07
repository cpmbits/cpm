from cpm.argument_parser import ArgumentParser
from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.publish_service import PublishService
from cpm.domain.project_packager import PackagingFailure
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound
from cpm.infrastructure.cpm_hub_connector_v1 import CpmHubConnectorV1
from cpm.infrastructure.cpm_hub_connector_v1 import InvalidCpmHubUrl
from cpm.infrastructure.cpm_hub_connector_v1 import AuthenticationFailure
from cpm.infrastructure.cpm_hub_connector_v1 import PublicationFailure
from cpm.infrastructure.http_client import HttpConnectionError


def publish_project(publish_service, publish_as_template=False):
    try:
        if publish_as_template:
            publish_service.publish_template()
        else:
            publish_service.publish()
    except ProjectDescriptorNotFound:
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
    publish_parser = argument_parser()
    args = publish_parser.parse_args(argv)

    cpm_hub_connector = CpmHubConnectorV1(repository_url=args.repository_url, dry_run=args.dry_run)
    service = PublishService(cpm_hub_connector)

    result = publish_project(service, publish_as_template=args.template)

    return result


def argument_parser():
    publish_parser = ArgumentParser(prog='cpm publish', description=description())
    publish_parser.add_argument('-s', '--repository-url',
                                required=True,
                                action='store',
                                help='URL of the cpm repository (default https://repo.cpmbits.com:8000)',
                                default='https://repo.cpmbits.com:8000')
    publish_parser.add_argument('-t', '--template',
                                required=False,
                                action='store_true',
                                help='publish the project as a template',
                                default=False)
    publish_parser.add_argument('-d', '--dry-run',
                                required=False,
                                action='store_true',
                                help='package the project and try login but do not publish it yet',
                                default=False)
    return publish_parser


def print_help():
    return argument_parser().print_help()


def description():
    return 'publish the project'
