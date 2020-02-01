from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.test_service import NoTestsFound


def run_tests(test_service, recipe):
    try:
        test_service.run_tests(recipe)
    except NotAChromosProject:
        return Result(FAIL, f'error: not a Chromos project')
    except NoTestsFound:
        return Result(FAIL, f'no tests to run')
    except CompilationError:
        return Result(FAIL, f'failed to compile tests')

    return Result(OK, f'Tests finished')
