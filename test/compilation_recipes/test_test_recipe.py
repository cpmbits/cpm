import unittest
from subprocess import CompletedProcess

from mock import MagicMock
from mock import call
from mock import patch

from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.compilation_recipes.test_recipe import TestRecipe
from cpm.domain.plugin import Plugin
from cpm.domain.project import Project
from cpm.domain.project import Package


class TestTestRecipe(unittest.TestCase):
    def test_recipe_creation(self):
        filesystem = MagicMock()
        TestRecipe(filesystem)

    def test_recipe_generation(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        project = self.xWingConsoleFrontendWithOneTest()
        project.add_include_directory('plugins/cest')
        recipe = TestRecipe(filesystem)

        recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/tests')
        filesystem.create_file.assert_called_once_with(
            'recipes/tests/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'set(PROJECT_NAME xWingConsoleFrontend)\n'
            'project(${PROJECT_NAME})\n'
            'include_directories(plugins/cest)\n'
            'add_library(${PROJECT_NAME}_test_library OBJECT )\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:${PROJECT_NAME}_test_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'set(UNIT_TEST_EXECUTABLES ${UNIT_TEST_EXECUTABLES} test_suite)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS ${UNIT_TEST_EXECUTABLES}\n'
            ')\n'

        )
        filesystem.symlink.assert_has_calls([
            call('../../plugins', 'recipes/tests/plugins'),
            call('../../tests', 'recipes/tests/tests'),
        ])

    def test_recipe_generation_with_one_package(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        project = self.xWingConsoleFrontendWithOneTest()
        project.add_package(Package('api'))
        recipe = TestRecipe(filesystem)

        recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/tests')
        filesystem.create_file.assert_called_once_with(
            'recipes/tests/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'set(PROJECT_NAME xWingConsoleFrontend)\n'
            'project(${PROJECT_NAME})\n'
            'include_directories()\n'
            'add_library(${PROJECT_NAME}_test_library OBJECT )\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:${PROJECT_NAME}_test_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'set(UNIT_TEST_EXECUTABLES ${UNIT_TEST_EXECUTABLES} test_suite)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS ${UNIT_TEST_EXECUTABLES}\n'
            ')\n'

        )
        filesystem.symlink.assert_has_calls([
            call('../../plugins', 'recipes/tests/plugins'),
            call('../../tests', 'recipes/tests/tests'),
            call('../../api', 'recipes/tests/api'),
        ])

    def test_recipe_is_updated_when_recipe_files_are_found(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = True
        project = self.xWingConsoleFrontendWithOneTest()
        test_recipe = TestRecipe(filesystem)

        test_recipe.generate(project)

        filesystem.create_directory.assert_not_called()
        filesystem.symlink.assert_not_called()

    @patch('subprocess.run')
    def test_recipe_compiles_with_cmake_and_ninja(self, subprocess_run):
        filesystem = MagicMock()
        project = self.xWingConsoleFrontendWithOneTest()
        recipe = TestRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, 0)]

        recipe.compile(project)

        subprocess_run.assert_has_calls([
            call(
                [recipe.CMAKE_COMMAND, '-G', 'Ninja', '.'],
                cwd='recipes/tests'
            ),
            call(
                ['ninja', 'unit'],
                cwd='recipes/tests'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_raises_exception_upon_cmake_generation_failure(self, subprocess_run):
        filesystem = MagicMock()
        project = self.xWingConsoleFrontendWithOneTest()
        recipe = TestRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, -1)]

        self.assertRaises(CompilationError, recipe.compile, project)

    @patch('subprocess.run')
    def test_recipe_raises_exception_upon_compilation_failure(self, subprocess_run):
        filesystem = MagicMock()
        project = self.xWingConsoleFrontendWithOneTest()
        recipe = TestRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, -1)]

        self.assertRaises(CompilationError, recipe.compile, project)

    @patch('subprocess.run')
    def test_recipe_runs_list_of_generated_executable_for_project_with_one_test(self, subprocess_run):
        filesystem = MagicMock()
        project = self.xWingConsoleFrontendWithOneTest()
        recipe = TestRecipe(filesystem)
        recipe.executables = ['test_suite']

        recipe.run_tests(project)

        subprocess_run.assert_has_calls([
            call(
                ['./test_suite'],
                cwd='recipes/tests'
            )
        ])

    def xWingConsoleFrontendWithOneTest(self):
        project = Project('xWingConsoleFrontend')
        project.sources = ['main.cpp']
        project.tests = ['tests/test_suite.cpp']
        project.plugins = [Plugin('cest', {})]
        return project
