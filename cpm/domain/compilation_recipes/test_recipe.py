import subprocess

from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.compilation_recipes import RECIPES_DIRECTORY

TEST_DIRECTORY = f'{RECIPES_DIRECTORY}/tests'

CMAKE_RECIPE = (
    '''set(UNIT_TEST_EXECUTABLES {test_suite_executables})
add_custom_target(unit
    COMMAND echo "> Done"
    DEPENDS ${{UNIT_TEST_EXECUTABLES}}
)
''')

CMAKE_TEST_EXECUTABLE = (
    '''add_executable({test_suite_executable} {test_suite} $<TARGET_OBJECTS:${{PROJECT_NAME}}_test_library>)
set_target_properties({test_suite_executable} PROPERTIES COMPILE_FLAGS -std=c++11)''')


class TestRecipe(object):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem):
        self.cmake_recipe = 'cmake_minimum_required (VERSION 3.7)\n'
        self.filesystem = filesystem
        self.executables = []

    def generate(self, project):
        if not self.filesystem.directory_exists(TEST_DIRECTORY):
            self.filesystem.create_directory(TEST_DIRECTORY)
            self.filesystem.symlink('../../plugins', 'recipes/tests/plugins')
            self.filesystem.symlink('../../tests', 'recipes/tests/tests')
            for package in project.packages:
                self.filesystem.symlink(f'../../{package.path}', f'recipes/tests/{package.path}')
        self.executables = [test_file.split('/')[-1].split('.')[0] for test_file in project.tests]
        self.filesystem.create_file(
            f'{TEST_DIRECTORY}/CMakeLists.txt',
            self._cmake_minimum_required() +
            self._project(project) +
            self._include_directories(project) +
            self._project_library(project) +
            self._test_executables(project) +
            self._unit_custom_target()
        )

    def _cmake_minimum_required(self):
        return 'cmake_minimum_required (VERSION 3.7)\n'

    def _project(self, project):
        return f'set(PROJECT_NAME {project.name})\n' \
               f'project(${{PROJECT_NAME}})\n'

    def _include_directories(self, project):
        include_directories = ' '.join(project.include_directories)
        return f'include_directories({include_directories})\n'

    def _project_library(self, project):
        sources_list = ' '.join(filter(lambda x: x != "main.cpp", project.sources))
        return f'add_library(${{PROJECT_NAME}}_test_library OBJECT {sources_list})\n'

    def _test_executables(self, project):
        return ''.join([
            self._add_executable(executable, test_file) for executable, test_file in zip(self.executables, project.tests)
        ])

    def _add_executable(self, executable, test_file):
        return f'add_executable({executable} {test_file} $<TARGET_OBJECTS:${{PROJECT_NAME}}_test_library>)\n' \
               f'set_target_properties({executable} PROPERTIES COMPILE_FLAGS -std=c++11)\n'

    def _unit_custom_target(self):
        executables = ' '.join(self.executables)
        return f'add_custom_target(unit\n' \
               f'    COMMAND echo "> Done"\n' \
               f'    DEPENDS {executables}\n' \
               f')\n'

    def compile(self, project):
        generate_result = subprocess.run(
            [self.CMAKE_COMMAND, '-G', 'Ninja', '.'],
            cwd=TEST_DIRECTORY
        )
        if generate_result.returncode != 0:
            raise CompilationError('failed to generate CMake recipe')

        compile_result = subprocess.run(
            ['ninja', 'unit'],
            cwd=TEST_DIRECTORY
        )
        if compile_result.returncode != 0:
            raise CompilationError('compilation failed')

    def run_tests(self, project):
        test_results = [self._run_test(executable) for executable in self.executables]
        if any(result.returncode != 0 for result in test_results):
            raise TestsFailed('tests failed')

    def _run_test(self, executable):
        return subprocess.run(
            [f'./{executable}'],
            cwd=TEST_DIRECTORY
        )


class MacOsTestRecipe(TestRecipe):
    CMAKE_COMMAND = '/Applications/CMake.app/Contents/bin/cmake'


class TestsFailed(RuntimeError):
    pass
