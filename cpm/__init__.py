#!/usr/bin/env python3.7
import argparse
import importlib
import sys
import pkgutil
import pkg_resources
import datetime

import cpm.api
from cpm.api.project_actions import discover_project_actions
from cpm.infrastructure.project_action_runner import ProjectActionRunner


def main():
    actions = {}

    for api_action in api_actions():
        module = importlib.import_module(api_action.name)
        if hasattr(module, "execute"):
            actions[module_name(api_action)] = module

    for project_action in discover_project_actions():
        actions[project_action.name] = ProjectActionRunner(project_action.name, project_action.command)

    top_level_parser = argparse.ArgumentParser(description='cpm Package Manager')
    top_level_parser.add_argument('-v', '--version', action='version', version=f'cpm version {pkg_resources.require("cpm-cli")[0].version}')
    top_level_parser.add_argument('action', choices=list(actions.keys()) + ['list-actions'], nargs='?')
    args = top_level_parser.parse_args(sys.argv[1:2])

    if not args.action:
        top_level_parser.print_help()
        sys.exit(0)

    if args.action == 'list-actions':
        print(' '.join(actions.keys()))
        sys.exit(0)

    start_time = datetime.datetime.now()

    result = actions[args.action].execute(sys.argv[2:])

    elapsed_time = datetime.datetime.now() - start_time

    finish(result, elapsed_time)


def module_name(api_action):
    return api_action.name.split('.')[-1]


def api_actions():
    return list(pkgutil.iter_modules(cpm.api.__path__, cpm.api.__name__+'.'))


def finish(result, elapsed_time):
    print(f'cpm: {result.message}  (took {__format(elapsed_time)})')
    sys.exit(result.status_code)


def __format(elapsed_time):
    if elapsed_time.seconds >= 60:
        return '%dm %d.%ds' % (elapsed_time.seconds/60, elapsed_time.seconds % 60, elapsed_time.microseconds/1000)
    else:
        return '%d.%ds' % (elapsed_time.seconds, elapsed_time.microseconds/1000)


if __name__ == '__main__':
    main()
