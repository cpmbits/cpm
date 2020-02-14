import unittest
from subprocess import CompletedProcess

from mock import MagicMock
from mock import call
from mock import patch

from cpm.domain.compilation_recipes import CompilationError
from cpm.domain.compilation_recipes.test_recipe import TestRecipe, TestsFailed
from cpm.domain.plugin import Plugin
from cpm.domain.project import Project
from cpm.domain.project import Package


class TestTestRecipe(unittest.TestCase):
    def test_recipe_creation(self):
        filesystem = MagicMock()
        TestRecipe(filesystem)

    def test_recipe_generation_with_one_test_suite(self):
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
            'project(xWingConsoleFrontend)\n'
            'include_directories(plugins/cest)\n'
            'add_library(xWingConsoleFrontend_object_library OBJECT )\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:xWingConsoleFrontend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )
        filesystem.symlink.assert_has_calls([
            call('../../plugins', 'recipes/tests/plugins'),
            call('../../tests', 'recipes/tests/tests'),
        ])

    def test_recipe_generation_with_one_test_suite_with_target_link_libraries(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        project = self.xWingConsoleFrontendWithOneTest()
        project.add_include_directory('plugins/cest')
        project.add_library('pthread')
        project.add_library('rt')
        recipe = TestRecipe(filesystem)

        recipe.generate(project)

        filesystem.create_file.assert_called_once_with(
            'recipes/tests/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(xWingConsoleFrontend)\n'
            'include_directories(plugins/cest)\n'
            'add_library(xWingConsoleFrontend_object_library OBJECT )\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:xWingConsoleFrontend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'target_link_libraries(test_suite pthread rt)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_many_test_suites(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        project = self.xWingConsoleFrontendWithManyTests()
        recipe = TestRecipe(filesystem)

        recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/tests')
        filesystem.create_file.assert_called_once_with(
            'recipes/tests/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(xWingConsoleFrontend)\n'
            'include_directories()\n'
            'add_library(xWingConsoleFrontend_object_library OBJECT )\n'
            'add_executable(test_suite_1 tests/test_suite_1.cpp $<TARGET_OBJECTS:xWingConsoleFrontend_object_library>)\n'
            'set_target_properties(test_suite_1 PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_executable(test_suite_2 tests/test_suite_2.cpp $<TARGET_OBJECTS:xWingConsoleFrontend_object_library>)\n'
            'set_target_properties(test_suite_2 PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite_1 test_suite_2\n'
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
            'project(xWingConsoleFrontend)\n'
            'include_directories()\n'
            'add_library(xWingConsoleFrontend_object_library OBJECT )\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:xWingConsoleFrontend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )
        filesystem.symlink.assert_has_calls([
            call('../../plugins', 'recipes/tests/plugins'),
            call('../../tests', 'recipes/tests/tests'),
            call('../../api', 'recipes/tests/api'),
        ])

    def test_recipe_generation_with_one_package_with_cflags(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        project = self.xWingConsoleFrontendWithOneTest()
        project.add_package(Package('api', sources=['file.cpp'], cflags=['-std=c++11']))
        project.add_sources(['file.cpp'])
        recipe = TestRecipe(filesystem)

        recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/tests')
        filesystem.create_file.assert_called_once_with(
            'recipes/tests/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(xWingConsoleFrontend)\n'
            'include_directories()\n'
            'set_source_files_properties(file.cpp PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_library(xWingConsoleFrontend_object_library OBJECT file.cpp)\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:xWingConsoleFrontend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_many_packages_with_cflags(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        project = self.xWingConsoleFrontendWithOneTest()
        project.add_package(Package('api', sources=['api.cpp'], cflags=['-std=c++11']))
        project.add_package(Package('domain', sources=['domain.cpp'], cflags=['-Wall']))
        project.add_sources(['api.cpp', 'domain.cpp'])
        recipe = TestRecipe(filesystem)

        recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/tests')
        filesystem.create_file.assert_called_once_with(
            'recipes/tests/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(xWingConsoleFrontend)\n'
            'include_directories()\n'
            'set_source_files_properties(api.cpp PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'set_source_files_properties(domain.cpp PROPERTIES COMPILE_FLAGS -Wall)\n'
            'add_library(xWingConsoleFrontend_object_library OBJECT api.cpp domain.cpp)\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:xWingConsoleFrontend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_custom_target(unit\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

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
        recipe = TestRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, 0)]

        recipe.compile()

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
        recipe = TestRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, -1)]

        self.assertRaises(CompilationError, recipe.compile)

    @patch('subprocess.run')
    def test_recipe_raises_exception_upon_compilation_failure(self, subprocess_run):
        filesystem = MagicMock()
        recipe = TestRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, -1)]

        self.assertRaises(CompilationError, recipe.compile)

    @patch('subprocess.run')
    def test_recipe_runs_list_of_generated_executable_for_project_with_one_test(self, subprocess_run):
        filesystem = MagicMock()
        recipe = TestRecipe(filesystem)
        recipe.executables = ['test_suite']
        subprocess_run.return_value = CompletedProcess(None, 0)

        recipe.run_tests()

        subprocess_run.assert_has_calls([
            call(
                ['./test_suite'],
                cwd='recipes/tests'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_runs_list_of_generated_executables_for_project_with_many_tests(self, subprocess_run):
        filesystem = MagicMock()
        recipe = TestRecipe(filesystem)
        recipe.executables = ['test_suite_1', 'test_suite_2']
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, 0)]

        recipe.run_tests()

        subprocess_run.assert_has_calls([
            call(
                ['./test_suite_1'],
                cwd='recipes/tests'
            ),
            call(
                ['./test_suite_2'],
                cwd='recipes/tests'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_raises_exception_when_test_execution_fails_in_project_with_one_test(self, subprocess_run):
        filesystem = MagicMock()
        recipe = TestRecipe(filesystem)
        recipe.executables = ['test_suite']
        subprocess_run.return_value = CompletedProcess(None, -1)

        self.assertRaises(TestsFailed, recipe.run_tests)

    @patch('subprocess.run')
    def test_recipe_runs_all_tests_before_raising_exception_when_tests_fail(self, subprocess_run):
        filesystem = MagicMock()
        recipe = TestRecipe(filesystem)
        recipe.executables = ['test_suite_1', 'test_suite_2']
        subprocess_run.side_effect = [CompletedProcess(None, -1), CompletedProcess(None, 0)]

        self.assertRaises(TestsFailed, recipe.run_tests)

        subprocess_run.assert_has_calls([
            call(
                ['./test_suite_1'],
                cwd='recipes/tests'
            ),
            call(
                ['./test_suite_2'],
                cwd='recipes/tests'
            )
        ])

    def xWingConsoleFrontendWithOneTest(self):
        project = Project('xWingConsoleFrontend')
        project.sources = ['main.cpp']
        project.tests = ['tests/test_suite.cpp']
        project.plugins = [Plugin('cest', {})]
        return project

    def xWingConsoleFrontendWithManyTests(self):
        project = Project('xWingConsoleFrontend')
        project.sources = ['main.cpp']
        project.tests = ['tests/test_suite_1.cpp', 'tests/test_suite_2.cpp']
        project.plugins = [Plugin('cest', {})]
        return project
