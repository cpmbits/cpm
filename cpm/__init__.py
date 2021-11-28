#!/usr/bin/env python3.7
import importlib
import sys
import pkgutil
import pkg_resources
import datetime
import argparse

from cpm.argument_parser import ArgumentParser
import cpm.api


def main():
    commands = available_commands()
    top_level_parser = argument_parser(commands)

    args = top_level_parser.parse_args(sys.argv[1:])

    if not args.command:
        print_help(top_level_parser, commands)
        sys.exit(0)

    command_to_execute = args.command[0]
    command_arguments = args.command[1:]

    if command_to_execute == 'help':
        if len(command_arguments) == 0:
            print_help(top_level_parser, commands)
        else:
            commands[args.command[1]].print_help()
            print()
        sys.exit(0)

    if command_to_execute not in commands:
        print(f'cpm: error: unknown command \'{command_to_execute}\', see \'cpm help\' for a list of available commands')
        sys.exit(1)

    start_time = datetime.datetime.now()

    result = commands[command_to_execute].execute(command_arguments)

    elapsed_time = datetime.datetime.now() - start_time

    finish(result, elapsed_time)


def available_commands():
    commands = {}
    for api_action in api_commands():
        module = importlib.import_module(api_action.name)
        if hasattr(module, 'execute'):
            commands[module_name(api_action)] = module
    return commands


def argument_parser(commands):
    top_level_parser = ArgumentParser(description='cpm: a modern project management tool for C/C++ projects')
    top_level_parser.add_argument('-v', '--version',
                                  action='version',
                                  help='show version and exit',
                                  version=f'cpm version {pkg_resources.require("cpm-cli")[0].version}')
    top_level_parser.add_argument('command',
                                  choices=list(commands.keys()) + ['help'],
                                  nargs=argparse.REMAINDER)
    return top_level_parser


def print_help(top_level_parser, commands):
    help_text = 'Usage: cpm [-h | --help] [-v | --version] <command> [args]'

    help_text += '\n\nOptional Arguments:'
    for option in top_level_parser.options:
        if 'command' in option['flags']:
            continue
        help_text += f'\n\t{", ".join(option["flags"]):<20}{option["help"]}'

    help_text += '\n\nAvailable commands:'
    for command in sorted(commands.keys()):
        help_text += f'\n\t{command:<20}{commands[command].description()}'

    help_text += '\n\nYou can get more detailed help about any specific command by running:\ncpm help <command>'
    help_text += '\n\n'

    print(help_text)


def module_name(api_command):
    return api_command.name.split('.')[-1]


def api_commands():
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
