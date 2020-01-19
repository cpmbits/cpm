import argparse
import sys

from cpm.api import create
from cpm.api import target
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.target_service import TargetService
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def __main():
    action = {
        'create': __create,
        'target': __target,
    }

    action_parser = argparse.ArgumentParser(description='Chromos Package Manager')
    action_parser.add_argument('action', choices=action.keys())
    args = action_parser.parse_args(sys.argv[1:2])

    action[args.action]()


def __finish(result):
    print(result.message)
    sys.exit(result.status_code)


def __create():
    create_parser = argparse.ArgumentParser(prog='cpm create', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('project_name')
    create_parser.add_argument('-s', '--include-sample-code', required=False, action='store_true', default=False)
    args = create_parser.parse_args(sys.argv[2:])

    constructor = CreationService(Filesystem())
    options = CreationOptions(include_sample_code=args.include_sample_code)
    result = create.new_project(constructor, args.project_name, options)

    __finish(result)


def __target():
    target_action = {
        'add': __add_target,
    }
    target_parser = argparse.ArgumentParser(prog='cpm target', description='Chromos Package Manager', add_help=False)
    target_parser.add_argument('target_action', choices=target_action.keys())
    args = target_parser.parse_args(sys.argv[2:3])

    target_action[args.target_action]()


def __add_target():
    add_target_parser = argparse.ArgumentParser(prog='cpm target add', description='Chromos Package Manager', add_help=False)
    add_target_parser.add_argument('target_name')
    args = add_target_parser.parse_args(sys.argv[3:])

    yaml_loader = YamlHandler(Filesystem())
    loader = ProjectLoader(yaml_loader)
    targets = TargetService(loader)

    result = target.add(targets, args.target_name)

    __finish(result)


__main()
