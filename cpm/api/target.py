import argparse
import sys

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.target_service import TargetService
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.project_loader import ProjectLoader
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def add_target(target_service, target_name):
    try:
        target_service.add_target(target_name)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')

    return Result(OK, f'Target {target_name} added to project')


def execute(argv):
    target_action = {
        'add': target_add,
    }
    target_parser = argparse.ArgumentParser(prog='cpm target', description='Chromos Package Manager',
                                            add_help=False)
    target_parser.add_argument('target_action', choices=target_action.keys())
    args = target_parser.parse_args(sys.argv[2:3])

    result = target_action[args.target_action]()

    return result


def target_add():
    add_target_parser = argparse.ArgumentParser(prog='cpm target add', description='Chromos Package Manager',
                                                add_help=False)
    add_target_parser.add_argument('target_name')
    args = add_target_parser.parse_args(sys.argv[3:])

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = TargetService(loader)

    result = add_target(service, args.target_name)

    return result