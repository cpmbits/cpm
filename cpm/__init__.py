#!/usr/bin/env python3.7
import argparse
import sys

from cpm.api.create import new_project
from cpm.api.target import add_target
from cpm.api.build import build_project
from cpm.api.clean import clean_project
from cpm.api.test import run_tests
from cpm.domain.build_service import BuildService
from cpm.domain.clean_service import CleanService
from cpm.domain.compilation_recipes.build import BuildRecipe
from cpm.domain.compilation_recipes.test_recipe import TestRecipe
from cpm.domain.creation_service import CreationService
from cpm.domain.creation_service import CreationOptions
from cpm.domain.project_loader import ProjectLoader
from cpm.domain.target_service import TargetService
from cpm.domain.test_service import TestService
from cpm.infrastructure.filesystem import Filesystem
from cpm.infrastructure.yaml_handler import YamlHandler


def main():
    action = {
        'create': create,
        'build': build,
        'clean': clean,
        'target': target,
        'test': test,
    }

    action_parser = argparse.ArgumentParser(description='Chromos Package Manager')
    action_parser.add_argument('action', choices=action.keys())
    args = action_parser.parse_args(sys.argv[1:2])

    action[args.action]()


def create():
    create_parser = argparse.ArgumentParser(prog='cpm create', description='Chromos Package Manager', add_help=False)
    create_parser.add_argument('project_name')
    create_parser.add_argument('-s', '--no-sample-code', required=False, action='store_true', default=False)
    args = create_parser.parse_args(sys.argv[2:])

    service = CreationService(Filesystem())
    options = CreationOptions(generate_sample_code=not args.no_sample_code)
    result = new_project(service, args.project_name, options)

    finish(result)


def build():
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = BuildService(loader)
    recipe = BuildRecipe(filesystem)

    result = build_project(service, recipe)

    finish(result)


def clean():
    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = CleanService(filesystem, loader)

    result = clean_project(service)

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

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = TargetService(loader)

    result = add_target(service, args.target_name)

    finish(result)


def test():
    add_target_parser = argparse.ArgumentParser(prog='cpm test', description='Chromos Package Manager', add_help=False)
    add_target_parser.add_argument('patterns', nargs=argparse.REMAINDER)
    args = add_target_parser.parse_args(sys.argv[2:])

    filesystem = Filesystem()
    yaml_handler = YamlHandler(filesystem)
    loader = ProjectLoader(yaml_handler, filesystem)
    service = TestService(loader)
    recipe = TestRecipe(filesystem)

    result = run_tests(service, recipe, args.patterns)

    finish(result)


def finish(result):
    print(f'CPM: {result.message}')
    sys.exit(result.status_code)
