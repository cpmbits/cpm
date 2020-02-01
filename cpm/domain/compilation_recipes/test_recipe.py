import subprocess

from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.compilation_recipes import RECIPES_DIRECTORY

TEST_DIRECTORY = f'{RECIPES_DIRECTORY}/tests'
CMAKE_RECIPE = (
    '''cmake_minimum_required (VERSION 3.7)
set(PROJECT_NAME {project_name})
project(${{PROJECT_NAME}})
include_directories({include_directories})
add_library(${{PROJECT_NAME}}_test_library OBJECT {sources_list})
add_executable({test_suite_executable} {test_suite} $<TARGET_OBJECTS:${{PROJECT_NAME}}_test_library>)
set_target_properties({test_suite_executable} PROPERTIES COMPILE_FLAGS -std=c++11)
set(UNIT_TEST_EXECUTABLES ${{UNIT_TEST_EXECUTABLES}} {test_suite_executable})
add_custom_target(unit
    COMMAND echo "> Done"
    DEPENDS ${{UNIT_TEST_EXECUTABLES}}
)
'''
)


class TestRecipe(object):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem):
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
            CMAKE_RECIPE.format(
                project_name=project.name,
                include_directories=' '.join(project.include_directories),
                sources_list=' '.join(filter(lambda x: x != 'main.cpp', project.sources)),
                test_suite_executable=self.executables[0],
                test_suite=project.tests[0]
            )
        )

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
        subprocess.run(
            [f'./{self.executables[0]}'],
            cwd=TEST_DIRECTORY
        )


class MacOsTestRecipe(TestRecipe):
    CMAKE_COMMAND = '/Applications/CMake.app/Contents/bin/cmake'
