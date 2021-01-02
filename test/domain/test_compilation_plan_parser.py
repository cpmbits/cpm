import unittest

from cpm.domain.project import project_descriptor_parser
from cpm.domain.project.project_descriptor import DeclaredBit, CompilationPlan, PackageDescription


class TestCompilationPlanParser(unittest.TestCase):
    def test_parsing_empty_compilation_plan(self):
        plan_description = {}
        compilation_plan = project_descriptor_parser.parse_compilation_plan(plan_description)
        assert compilation_plan == CompilationPlan()

    def test_parsing_compilation_plan_with_declared_bits(self):
        plan_description = {
            'bits': {
                'sqlite3': '1.0',
                'base64': '3.22'
            }
        }
        compilation_plan = project_descriptor_parser.parse_compilation_plan(plan_description)
        assert compilation_plan.declared_bits == [DeclaredBit('sqlite3', '1.0'), DeclaredBit('base64', '3.22')]

    def test_parsing_compilation_plan_with_declared_packages(self):
        plan_description = {
            'packages': {
                'cpmhub/bits': {},
                'cpmhub/http': {}
            }
        }
        compilation_plan = project_descriptor_parser.parse_compilation_plan(plan_description)
        assert compilation_plan.packages == [PackageDescription('cpmhub/bits'), PackageDescription('cpmhub/http')]

    def test_parsing_compilation_plan_with_declared_packages_with_cflags(self):
        plan_description = {
            'packages': {
                'cpmhub/bits': {
                    'cflags': ['-O2']
                },
            }
        }
        compilation_plan = project_descriptor_parser.parse_compilation_plan(plan_description)
        assert compilation_plan.packages == [PackageDescription('cpmhub/bits', cflags=['-O2'])]

    def test_parsing_compilation_plan_with_flags_and_libraries(self):
        plan_description = {
            'cflags': ['-O0'],
            'libraries': ['pthread']
        }
        compilation_plan = project_descriptor_parser.parse_compilation_plan(plan_description)
        assert compilation_plan.cflags == ['-O0']
        assert compilation_plan.libraries == ['pthread']

