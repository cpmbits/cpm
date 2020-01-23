import subprocess

from cpm.domain.compilation_recipes import RECIPES_DIRECTORY

TEST_DIRECTORY = f'{RECIPES_DIRECTORY}/tests'
CMAKE_RECIPE = (
    '''cmake_minimum_required (VERSION 3.7)
set(PROJECT_NAME {project_name})
project(${{PROJECT_NAME}})
include_directories(sources)
add_library(${{PROJECT_NAME}}_test_library OBJECT {sources_list})
add_executable({test_suite_executable} {test_suite} $<TARGET_OBJECTS:${{PROJECT_NAME}}_test_library>)
'''
)


class TestRecipe(object):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.executables = []

    def generate(self, project):
        self.filesystem.create_directory(TEST_DIRECTORY)
        self.filesystem.symlink('../../sources', 'recipes/tests/sources')
        self.executables = [project.tests[0].split('/')[-1].split('.')[0]]
        self.filesystem.create_file(
            f'{TEST_DIRECTORY}/CMakeLists.txt',
            CMAKE_RECIPE.format(
                project_name=project.name,
                sources_list=' '.join(project.sources),
                test_suite_executable=self.executables[0],
                test_suite=project.tests[0]
            )
        )

    def compile(self, project):
        subprocess.run(
            [self.CMAKE_COMMAND, '-G', 'Ninja', '.'],
            cwd=TEST_DIRECTORY
        )
        subprocess.run(
            ['ninja', project.name],
            cwd=TEST_DIRECTORY
        )

    def run_tests(self, project):
        subprocess.run(
            [self.executables[0]],
            cwd=TEST_DIRECTORY
        )


class MacOsTestRecipe(object):
    CMAKE_COMMAND = '/Applications/CMake.app/Contents/bin/cmake'
