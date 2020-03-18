#!/usr/bin/env python3.7
import argparse
import importlib
import sys
import pkgutil

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

    action_parser = argparse.ArgumentParser(description='Chromos Package Manager')
    action_parser.add_argument('action', choices=list(actions.keys()) + ['list-actions'])
    args = action_parser.parse_args(sys.argv[1:2])

    if args.action == 'list-actions':
        print(' '.join(actions.keys()))
        sys.exit(0)

    result = actions[args.action].execute(sys.argv[2:])

    finish(result)


def module_name(api_action):
    return api_action.name.split('.')[-1]


def api_actions():
    return list(pkgutil.iter_modules(cpm.api.__path__, cpm.api.__name__+'.'))


def finish(result):
    print(f'CPM: {result.message}')
    sys.exit(result.status_code)
