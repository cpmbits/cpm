from cpm.api.result import Result
from cpm.api.result import OK
from cpm.api.result import FAIL
from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.compilation_recipes.test_recipe import TestsFailed
from cpm.domain.project_loader import NotAChromosProject
from cpm.domain.test_service import NoTestsFound


def run_tests(test_service, recipe, patterns=[]):
    try:
        test_service.run_tests(recipe, patterns)
    except NotAChromosProject:
        return Result(FAIL, 'not a Chromos project')
    except CompilationError as e:
        return Result(FAIL, f'{str(e)}')
    except TestsFailed:
        return Result(FAIL, '✖ FAIL')
    except NoTestsFound:
        return Result(OK, 'no tests to run')

    return Result(OK, '✔ PASS')
