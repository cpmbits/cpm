import subprocess
import signal

from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.compilation_recipes import RECIPES_DIRECTORY
from cpm.domain.compilation_recipes import cmake

TEST_DIRECTORY = f'{RECIPES_DIRECTORY}/tests'


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
            self.build_cmakelists(project)
        )

    def build_cmakelists(self, project):
        project_object_library = project.name + '_object_library'
        cmake_builder = cmake.a_cmake() \
            .minimum_required('3.7') \
            .project(project.name) \
            .include(project.include_directories)

        for package in project.packages:
            if package.cflags:
                cmake_builder.set_source_files_properties(package.sources, 'COMPILE_FLAGS', package.cflags)
        cmake_builder.add_object_library(project_object_library, self._sources_without_main(project))
        for executable, test_file in zip(self.executables, project.tests):
            cmake_builder.add_executable(executable, [test_file], [project_object_library]) \
                         .set_target_properties(executable, 'COMPILE_FLAGS', ['-std=c++11'])
            if project.link_options.libraries:
                cmake_builder.target_link_libraries(executable, project.link_options.libraries)
        cmake_builder.add_custom_target('unit', 'echo "> Done', self.executables)
        return cmake_builder.contents

    def _sources_without_main(self, project):
        return filter(lambda x: x != "main.cpp", project.sources)

    def compile(self):
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

    def run_tests(self):
        test_results = [self.run_test(executable) for executable in self.executables]
        if any(result.returncode != 0 for result in test_results):
            raise TestsFailed('tests failed')

    def run_test(self, executable):
        result = subprocess.run(
            [f'./{executable}'],
            cwd=TEST_DIRECTORY
        )
        if result.returncode < 0:
            print(f'{executable} failed with signal {result.returncode} ({signal.Signals(-result.returncode).name})')
        return result


class TestsFailed(RuntimeError):
    pass
