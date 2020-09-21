import unittest

from mock import MagicMock
from mock import call
from mock import patch

from subprocess import CompletedProcess
from cpm.domain.cmake_recipe import CMakeRecipe, TestsFailed, BUILD_DIRECTORY, CMAKELISTS, CompilationError
from cpm.domain.bit import Bit
from cpm.domain.project import Project, Package


class TestCMakeRecipe(unittest.TestCase):
    def test_instantiation(self):
        filesystem = MagicMock()
        CMakeRecipe(filesystem)

    def test_recipe_generation_without_bits_or_packages(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
        )

    def test_recipe_generation_with_target_link_libraries(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
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
        )

    def test_recipe_generation_with_one_package(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
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
        )

    def test_recipe_generation_with_one_package_with_global_compile_flags(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
        project.add_package(Package('package', sources=['package.cpp']))
        project.add_include_directory('package')
        project.add_sources(['package.cpp'])
        project.compile_flags = ['-g']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories(package)\n'
            'add_executable(DeathStarBackend main.cpp package.cpp)\n'
            'set_target_properties(DeathStarBackend PROPERTIES COMPILE_FLAGS "-g")\n'
        )

    def test_recipe_generation_with_one_package_with_cflags(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
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
        )

    def test_recipe_generation_with_many_packages_with_cflags(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
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
        )

    def test_recipe_generation_with_one_bit(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_one_bit('DeathStarBackend', sources=['bit.cpp'])
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_library(cest STATIC bit.cpp)\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'target_link_libraries(DeathStarBackend cest)\n'
        )

    def test_recipe_generation_with_one_bit_without_sources(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_one_bit('DeathStarBackend')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
        )

    def test_recipe_generation_with_one_bit_with_a_package_with_cflags(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_one_bit('DeathStarBackend', sources=['bit.cpp'], cflags=['-DDEFINE'])
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_library(cest STATIC bit.cpp)\n'
            'set_source_files_properties(bit.cpp PROPERTIES COMPILE_FLAGS "-DDEFINE")\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'target_link_libraries(DeathStarBackend cest)\n'
        )

    def test_recipe_generation_with_one_bit_and_link_libraries(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_one_bit('DeathStarBackend', sources=['bit.cpp'], cflags=['-DDEFINE'])
        project.add_library('boost')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_library(cest STATIC bit.cpp)\n'
            'set_source_files_properties(bit.cpp PROPERTIES COMPILE_FLAGS "-DDEFINE")\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'target_link_libraries(DeathStarBackend cest boost)\n'
        )

    def test_recipe_generation_with_one_test_suite(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_sources('DeathStarBackend', ['source.cpp'])
        project.tests = ['tests/test_suite.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp source.cpp)\n'
            'add_library(DeathStarBackend_object_library OBJECT source.cpp)\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_suite_and_one_bit_and_no_link_libraries(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_one_bit('DeathStarBackend', ['bit.cpp'])
        project.tests = ['tests/test_suite.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_library(cest STATIC bit.cpp)\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'target_link_libraries(DeathStarBackend cest)\n'
            'add_executable(test_suite tests/test_suite.cpp)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'target_link_libraries(test_suite cest)\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_suite_and_one_bit_and_link_libraries(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_one_bit('DeathStarBackend', ['bit.cpp'])
        project.tests = ['tests/test_suite.cpp']
        project.add_library('boost')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_library(cest STATIC bit.cpp)\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'target_link_libraries(DeathStarBackend cest boost)\n'
            'add_executable(test_suite tests/test_suite.cpp)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'target_link_libraries(test_suite cest boost)\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_many_test_suites(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_sources('DeathStarBackend', ['source.cpp'])
        project.tests = ['tests/test_suite_1.cpp', 'tests/test_suite_2.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp source.cpp)\n'
            'add_library(DeathStarBackend_object_library OBJECT source.cpp)\n'
            'add_executable(test_suite_1 tests/test_suite_1.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite_1 PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'add_executable(test_suite_2 tests/test_suite_2.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite_2 PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite_1 test_suite_2\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_with_target_link_libraries(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_sources('DeathStarBackend', ['source.cpp'])
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
            'add_executable(DeathStarBackend main.cpp source.cpp)\n'
            'target_link_libraries(DeathStarBackend pthread rt)\n'
            'add_library(DeathStarBackend_object_library OBJECT source.cpp)\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'target_link_libraries(test_suite pthread rt)\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_suite_with_project_without_sources(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('Cest')
        project.tests = ['tests/test_cest.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(Cest)\n'
            'include_directories()\n'
            'add_executable(Cest main.cpp)\n'
            'add_executable(test_cest tests/test_cest.cpp)\n'
            'set_target_properties(test_cest PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_cest\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_suite_and_test_include_directories(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_sources('DeathStarBackend', ['source.cpp'])
        project.test_include_directories = ['mocks', 'fakes']
        project.tests = ['tests/test_suite.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp source.cpp)\n'
            'add_library(DeathStarBackend_object_library OBJECT source.cpp)\n'
            'add_executable(test_suite tests/test_suite.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'target_include_directories(test_suite PUBLIC mocks fakes)\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_generation_with_one_test_suite_and_test_sources(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_with_sources('DeathStarBackend', ['source.cpp'])
        project.test_sources = ['mocks/mock.cpp', 'mocks/fake.cpp']
        project.tests = ['tests/test_suite.cpp']
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('build')
        filesystem.create_file.assert_called_once_with(
            'CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp source.cpp)\n'
            'add_library(DeathStarBackend_object_library OBJECT source.cpp)\n'
            'add_executable(test_suite tests/test_suite.cpp mocks/mock.cpp mocks/fake.cpp $<TARGET_OBJECTS:DeathStarBackend_object_library>)\n'
            'set_target_properties(test_suite PROPERTIES COMPILE_FLAGS "-std=c++11 -g")\n'
            'add_custom_target(tests\n'
            '    COMMAND echo "> Done"\n'
            '    DEPENDS test_suite\n'
            ')\n'
        )

    def test_recipe_is_updated_when_recipe_files_are_found(self):
        filesystem = self.filesystemMockWithRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
        cmake_recipe = CMakeRecipe(filesystem)

        cmake_recipe.generate(project)

        filesystem.create_directory.assert_not_called()
        filesystem.create_file.assert_called_once()

    @patch('subprocess.run')
    def test_recipe_builds_with_cmake_and_ninja(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
        cmake_recipe = CMakeRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, 0)]

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
    def test_build_raises_an_exception_when_cmake_command_fails(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
        cmake_recipe = CMakeRecipe(filesystem)
        subprocess_run.return_value = CompletedProcess(None, -1)

        self.assertRaises(CompilationError, cmake_recipe.build, project)

    @patch('subprocess.run')
    def test_build_raises_an_exception_when_ninja_command_fails(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = _project_without_sources('DeathStarBackend')
        cmake_recipe = CMakeRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, -1)]

        self.assertRaises(CompilationError, cmake_recipe.build, project)

    @patch('subprocess.run')
    def test_recipe_builds_tests_with_cmake_and_ninja(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        cmake_recipe = CMakeRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, 0)]

        cmake_recipe.build_tests()

        subprocess_run.assert_has_calls([
            call(
                [cmake_recipe.CMAKE_COMMAND, '-G', 'Ninja', '..'],
                cwd='build'
            ),
            call(
                ['ninja', 'tests'],
                cwd='build'
            )
        ])

    @patch('subprocess.run')
    def test_build_tests_raises_exception_when_cmake_command_fails(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        cmake_recipe = CMakeRecipe(filesystem)
        subprocess_run.return_value = CompletedProcess(None, -1)

        self.assertRaises(CompilationError, cmake_recipe.build_tests)

    @patch('subprocess.run')
    def test_build_tests_raises_exception_when_ninja_command_fails(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        cmake_recipe = CMakeRecipe(filesystem)
        subprocess_run.side_effect = [CompletedProcess(None, 0), CompletedProcess(None, -1)]

        self.assertRaises(CompilationError, cmake_recipe.build_tests)

    @patch('subprocess.run')
    def test_recipe_runs_list_of_generated_executable_for_project_with_one_test(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        recipe.test_executables = ['test_suite']
        subprocess_run.return_value = CompletedProcess(None, 0)

        recipe.run_all_tests()

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

        recipe.run_all_tests()

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

        self.assertRaises(TestsFailed, recipe.run_all_tests)

    @patch('subprocess.run')
    def test_recipe_runs_all_tests_before_raising_exception_when_tests_fail(self, subprocess_run):
        filesystem = MagicMock()
        recipe = CMakeRecipe(filesystem)
        recipe.test_executables = ['test_suite_1', 'test_suite_2']
        subprocess_run.side_effect = [CompletedProcess(None, -1), CompletedProcess(None, 0)]

        self.assertRaises(TestsFailed, recipe.run_all_tests)

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


def _project_without_sources(name):
    project = Project(name)
    project.sources = ['main.cpp']
    return project


def _project_with_one_bit(name, sources=[], cflags=[]):
    project = Project(name)
    project.sources = ['main.cpp']
    bit = Bit('cest')
    bit.add_package(Package('bits/cest', sources=sources, cflags=cflags))
    bit.add_sources(sources)
    project.add_bit(bit)
    return project


def _project_with_sources(name, sources):
    project = Project(name)
    project.sources = ['main.cpp'] + sources
    return project
