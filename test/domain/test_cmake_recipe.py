import unittest

from mock import MagicMock
from mock import call
from mock import patch

from subprocess import CompletedProcess
from cpm.domain.cmake_recipe import CMakeRecipe, TestsFailed, BUILD_DIRECTORY, CMAKELISTS
from cpm.domain.plugin import Plugin
from cpm.domain.project import Project, Package


class TestCMakeRecipe(unittest.TestCase):
    def test_instantiation(self):
        filesystem = MagicMock()
        CMakeRecipe(filesystem)

    def test_recipe_generation_without_plugins_or_packages(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_target_link_libraries(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.add_library('pthread')
        project.add_library('rt')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'target_link_libraries(DeathStarBackend pthread rt)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_one_package(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.add_package(Package('package'))
        project.add_include_directory('package')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories(package)\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_one_package_with_cflags(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.add_package(Package('package', cflags=['-std=c++11', '-DMACRO'], sources=['package.cpp']))
        project.add_include_directory('package')
        project.add_sources(['package.cpp'])
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories(package)\n'
            'set_source_files_properties(package.cpp PROPERTIES COMPILE_FLAGS "-std=c++11 -DMACRO")\n'
            'add_executable(DeathStarBackend main.cpp package.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_many_packages_with_cflags(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.add_package(Package('package1', cflags=['-std=c++11'], sources=['package1.cpp']))
        project.add_package(Package('package2', cflags=['-Wall'], sources=['package2.cpp']))
        project.add_include_directory('package')
        project.add_sources(['package1.cpp'])
        project.add_sources(['package2.cpp'])
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories(package)\n'
            'set_source_files_properties(package1.cpp PROPERTIES COMPILE_FLAGS "-std=c++11")\n'
            'set_source_files_properties(package2.cpp PROPERTIES COMPILE_FLAGS "-Wall")\n'
            'add_executable(DeathStarBackend main.cpp package1.cpp package2.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_one_plugin(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackendWithOnePlugin()
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_suite(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.tests = ['tests/test_suite.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
            'add_library(DeathStarBackend_object_library OBJECT )\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_custom_target(test\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_many_test_suites(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.tests = ['tests/test_suite_1.cpp', 'tests/test_suite_2.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
            'add_library(DeathStarBackend_object_library OBJECT )\n'
            'add_executable(test_suite_1 tests/test_suite_1.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite_1 PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_executable(test_suite_2 tests/test_suite_2.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite_2 PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'add_custom_target(test\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite_1 test_suite_2\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_with_target_link_libraries(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.tests = ['tests/test_suite.cpp']
        project.add_library('pthread')
        project.add_library('rt')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'target_link_libraries(DeathStarBackend pthread rt)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/DeathStarBackend\n'
            ')\n'
            'add_library(DeathStarBackend_object_library OBJECT )\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS -std=c++11)\n'
            'target_link_libraries(test_suite pthread rt)\n'
            'add_custom_target(test\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_is_updated_when_recipe_files_are_found(self):
        filesystem = self.filesystemMockWithRecipeFiles()
        project = self.deathStarBackend()
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_not_called()
        filesystem.create_file.assert_called_once()

    @patch('subprocess.run')
    def test_recipe_builds_with_cmake_and_ninja(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.build(project)

        subprocess_run.assert_has_calls([
            call(
                [cmake_recipe.CMAKE_COMMAND, '-G', 'Ninja', '..'],
                cwd='build'
            ),
            call(
                ['ninja', 'DeathStarBackend'],
                cwd='build'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_builds_tests_with_cmake_and_ninja(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.build_tests()

        subprocess_run.assert_has_calls([
            call(
                [cmake_recipe.CMAKE_COMMAND, '-G', 'Ninja', '..'],
                cwd='build'
            ),
            call(
                ['ninja', 'test'],
                cwd='build'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_runs_list_of_generated_executable_for_project_with_one_test(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        recipe.test_executables = ['test_suite']
        subprocess_run.return_value = CompletedProcess(None, 0)

        recipe.run_tests()

        subprocess_run.assert_has_calls([
            call(
                ['./test_suite'],
                cwd='build'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_runs_list_of_generated_executables_for_project_with_many_tests(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        recipe.test_executables = ['test_suite_1', 'test_suite_2']
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, 0)]

        recipe.run_tests()

        subprocess_run.assert_has_calls([
            call(
                ['./test_suite_1'],
                cwd='build'
            ),
            call(
                ['./test_suite_2'],
                cwd='build'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_raises_exception_when_test_execution_fails_in_project_with_one_test(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        recipe.test_executables = ['test_suite']
        subprocess_run.return_value = CompletedProcess(None, -1)

        self.assertRaises(TestsFailed, recipe.run_tests)

    @patch('subprocess.run')
    def test_recipe_runs_all_tests_before_raising_exception_when_tests_fail(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        recipe.test_executables = ['test_suite_1', 'test_suite_2']
        subprocess_run.side_effect = [CompletedProcess(None, -1), CompletedProcess(None, 0)]

        self.assertRaises(TestsFailed, recipe.run_tests)

        subprocess_run.assert_has_calls([
            call(
                ['./test_suite_1'],
                cwd='build'
            ),
            call(
                ['./test_suite_2'],
                cwd='build'
            )
        ])

    @patch('subprocess.run')
    def test_recipe_cleans_project_then_removes_build_directory(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        filesystem.directory_exists.return_value = True

        recipe.clean()

        subprocess_run.assert_has_calls([
            call(
                ['ninja', 'clean'],
                cwd='build'
            )
        ])
        filesystem.remove_directory.assert_called_once_with(BUILD_DIRECTORY)
        filesystem.delete_file.assert_called_once_with(CMAKELISTS)

    @patch('subprocess.run')
    def test_clean_is_not_run_if_build_directory_does_not_exist(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        filesystem.directory_exists.return_value = False

        recipe.clean()

        subprocess_run.assert_not_called()

    def deathStarBackend(self):
        project = Project('DeathStarBackend')
        project.sources = ['main.cpp']
        return project

    def deathStarBackendWithOnePlugin(self):
        project = Project('DeathStarBackend')
        project.sources = ['main.cpp']
        project.add_plugin(Plugin('cest', '1.0'))
        return project

    def filesystemMockWithoutRecipeFiles(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = False
        filesystem.file_exists.return_value = False
        return filesystem

    def filesystemMockWithRecipeFiles(self):
        filesystem = MagicMock()
        filesystem.directory_exists.return_value = True
        filesystem.file_exists.return_value = True
        return filesystem

