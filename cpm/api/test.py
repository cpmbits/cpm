from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.compilation_recipes.test_recipe import TestsFailed
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.test_service import NoTestsFound


def run_tests(test_service, recipe):
    try:
        test_service.run_tests(recipe)
    except NotAChromosProject:
        return Result(FAIL, f'not a Chromos project')
    except CompilationError:
        return Result(FAIL, f'✖ failed to compile tests')
    except TestsFailed:
        return Result(FAIL, f'✖ tests failed')
    except NoTestsFound:
        return Result(OK, f'no tests to run')

    return Result(OK, f'✔ Tests passed')
