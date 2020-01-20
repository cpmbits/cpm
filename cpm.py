#!/usr/local/bin/python3.7
import argparse
import sys

from cpm.api.create import new_project
from cpm.api.target import add_target
from cpm.api.build import build_project
from cpm.domain.build_service import BuildService
from cpm.domain.compilation_recipes.build import BuildRecipe
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.target_service import TargetService
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def main():
    action = {
        'create': create,
        'build': build,
        'target': target,
    }

    action_parser = argparse.ArgumentParser(description='Chromos Package Manager')
    action_parser.add_argument('action', choices=action.keys())
    args = action_parser.parse_args(sys.argv[1:2])

    action[args.action]()


def create():
    create_parser = argparse.ArgumentParser(prog='cpm create', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('project_name')
    create_parser.add_argument('-s', '--generate-sample-code', required=False, action='store_true', default=False)
    args = create_parser.parse_args(sys.argv[2:])

    service = CreationService(Filesystem())
    options = CreationOptions(generate_sample_code=args.generate_sample_code)
    result = new_project(service, args.project_name, options)

    finish(result)


def build():
    filesystem = Filesystem()
    yaml_loader = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_loader)
    service = BuildService(loader)
    recipe = BuildRecipe(filesystem)

    result = build_project(service, recipe)

    finish(result)


def target():
    target_action = {
        'add': target_add,
    }
    target_parser = argparse.ArgumentParser(prog='cpm target', description='Chromos Package Manager', add_help=False)
    target_parser.add_argument('target_action', choices=target_action.keys())
    args = target_parser.parse_args(sys.argv[2:3])

    target_action[args.target_action]()


def target_add():
    add_target_parser = argparse.ArgumentParser(prog='cpm target add', description='Chromos Package Manager', add_help=False)
    add_target_parser.add_argument('target_name')
    args = add_target_parser.parse_args(sys.argv[3:])

    yaml_loader = YamlHandler(Filesystem())
    loader = ProjectLoader(yaml_loader)
    service = TargetService(loader)

    result = add_target(service, args.target_name)

    finish(result)


def finish(result):
    print(result.message)
    sys.exit(result.status_code)


main()
