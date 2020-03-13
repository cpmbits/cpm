#!/usr/bin/env python3.7
import argparse
import importlib
import sys
import pkgutil

import cpm.api


def main():
    action = {}
    for api_action in api_actions():
        module = importlib.import_module(api_action.name)
        action[module_name(api_action)] = module

    action_parser = argparse.ArgumentParser(description='Chromos Package Manager')
    action_parser.add_argument('action', choices=action.keys())
    args = action_parser.parse_args(sys.argv[1:2])

    result = action[args.action].execute(sys.argv[2:])

    finish(result)


def module_name(api_action):
    return api_action.name.split('.')[-1]


def api_actions():
    return list(pkgutil.iter_modules(cpm.api.__path__, cpm.api.__name__+'.'))


def finish(result):
    print(f'CPM: {result.message}')
    sys.exit(result.status_code)
