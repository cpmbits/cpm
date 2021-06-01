import argparse

from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.project.project_loader import ProjectLoader
from cpm.domain.project.project_descriptor_parser import ProjectDescriptorNotFound
from cpm.domain.test_service import TestService
from cpm.domain.test_service import NoTestsFound
from cpm.domain.project_commands import BuildError
from cpm.domain.project_commands import TestsFailed
from cpm.domain.project_commands import ProjectCommands


def run_tests(test_service, files_or_dirs=(), test_args=(), target='default'):
    try:
        test_service.run_tests(files_or_dirs, target, test_args)
    except ProjectDescriptorNotFound:
        return Result(FAIL, 'error: not a cpm project')
    except BuildError as e:
        return Result(FAIL, f'error: failed building tests')
    except TestsFailed:
        return Result(FAIL, '✖ FAIL')
    except NoTestsFound:
        return Result(OK, 'no tests to run')

    return Result(OK, '✔ PASS')


def execute(argv):
    add_target_parser = argparse.ArgumentParser(prog='cpm test', description='cpm, modern C/C++ system', add_help=False)
    add_target_parser.add_argument('rest', nargs=argparse.REMAINDER)
    args = add_target_parser.parse_args(argv)

    project_loader = ProjectLoader()
    cmakelists_builder = CMakeListsBuilder()
    project_commands = ProjectCommands()
    service = TestService(project_loader, cmakelists_builder, project_commands)
    files_or_dirs, test_args = __parse_rest(args.rest)

    result = run_tests(service, files_or_dirs, test_args)

    return result


def __parse_rest(rest):
    try:
        delimiter_index = rest.index('--')
        files_or_dirs = rest[:delimiter_index]
        test_args = rest[delimiter_index+1:]
    except ValueError:
        files_or_dirs = rest
        test_args = []
    return files_or_dirs, test_args
