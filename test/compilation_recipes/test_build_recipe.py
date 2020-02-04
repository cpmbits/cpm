import unittest
import mock

from cpm.domain.compilation_recipes.build import BuildRecipe
from cpm.domain.compilation_recipes.build import MacOsBuildRecipe
from cpm.domain.plugin import Plugin
from cpm.domain.project import Project, Package


class TestBuildRecipe(unittest.TestCase):
    def test_instantiation(self):
        filesystem = mock.MagicMock()
        BuildRecipe(filesystem)

    def test_recipe_generation_without_plugins_or_packages(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/build')
        filesystem.symlink.assert_called_once_with('../../main.cpp', 'recipes/build/main.cpp')
        filesystem.create_file.assert_called_once_with(
            'recipes/build/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/../../DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_one_package(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        project.add_package(Package('package'))
        project.add_include_directory('package')
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/build')
        filesystem.symlink.assert_has_calls([
            mock.call('../../main.cpp', 'recipes/build/main.cpp'),
            mock.call('../../package', 'recipes/build/package'),
        ])
        filesystem.create_file.assert_called_once_with(
            'recipes/build/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories(package)\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/../../DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_generation_with_one_plugin(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackendWithOnePlugin()
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/build')
        filesystem.symlink.assert_has_calls([
            mock.call('../../main.cpp', 'recipes/build/main.cpp'),
            mock.call('../../plugins', 'recipes/build/plugins')
        ])
        filesystem.create_file.assert_called_once_with(
            'recipes/build/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'project(DeathStarBackend)\n'
            'include_directories()\n'
            'add_executable(DeathStarBackend main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET DeathStarBackend\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:DeathStarBackend> ${PROJECT_SOURCE_DIR}/../../DeathStarBackend\n'
            ')\n'
        )

    def test_recipe_is_updated_when_recipe_files_are_found(self):
        filesystem = self.filesystemMockWithRecipeFiles()
        project = self.deathStarBackend()
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_not_called()
        filesystem.create_file.assert_called_once()

    @mock.patch('subprocess.run')
    def test_recipe_compiles_with_cmake_and_ninja(self, subprocess_run):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        build_recipe = MacOsBuildRecipe(filesystem)

        build_recipe.compile(project)

        subprocess_run.assert_has_calls([
            mock.call(
                [build_recipe.CMAKE_COMMAND, '-G', 'Ninja', '.'],
                cwd='recipes/build'
            ),
            mock.call(
                ['ninja', 'DeathStarBackend'],
                cwd='recipes/build'
            )
        ])

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
        filesystem = mock.MagicMock()
        filesystem.directory_exists.return_value = False
        filesystem.file_exists.return_value = False
        return filesystem

    def filesystemMockWithRecipeFiles(self):
        filesystem = mock.MagicMock()
        filesystem.directory_exists.return_value = True
        filesystem.file_exists.return_value = True
        return filesystem

