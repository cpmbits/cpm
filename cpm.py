import argparse
import sys

from cpm.api import create
from cpm.domain.project_constructor import ProjectConstructor
from cpm.infrastructure.filesystem import Filesystem


def __finish(result):
    print(result.message)
    sys.exit(result.status_code)


def __create():
    create_parser = argparse.ArgumentParser(prog='cpm create', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('project_name')
    args = create_parser.parse_args(sys.argv[2:])

    constructor = ProjectConstructor(Filesystem())
    result = create.new_project(constructor, args.project_name)

    __finish(result)


def __main():
    action_parser = argparse.ArgumentParser(description='Chromos Package Manager')
    action_parser.add_argument('action', choices=['create'])
    args = action_parser.parse_args(sys.argv[1:2])

    action = {
        'create': __create,
    }
    action[args.action]()


__main()
