import unittest
import mock

from cpm.domain.compilation_recipes.build import BuildRecipe
from cpm.domain.compilation_recipes.build import MacOsBuildRecipe
from cpm.domain.project import Project


class TestBuildRecipe(unittest.TestCase):
    def test_instantiation(self):
        filesystem = mock.MagicMock()
        BuildRecipe(filesystem)

    def test_recipe_generation_without_plugins(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/build')
        filesystem.symlink.assert_called_once_with('../../sources', 'recipes/build/sources')
        filesystem.create_file.assert_called_once_with(
            'recipes/build/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'set(PROJECT_NAME DeathStarBackend)\n'
            'project(${PROJECT_NAME})\n'
            'include_directories(sources)\n'
            'add_executable(${PROJECT_NAME} sources/main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET ${PROJECT_NAME}\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${PROJECT_NAME}> ${PROJECT_SOURCE_DIR}/../../${PROJECT_NAME}\n'
            ')\n'
        )

    def test_recipe_generation_with_plugins(self):
        filesystem = self.filesystemMockWithoutRecipeFiles()
        project = self.deathStarBackend()
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/build')
        filesystem.symlink.assert_called_once_with('../../sources', 'recipes/build/sources')
        filesystem.create_file.assert_called_once_with(
            'recipes/build/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'set(PROJECT_NAME DeathStarBackend)\n'
            'project(${PROJECT_NAME})\n'
            'include_directories(sources)\n'
            'add_executable(${PROJECT_NAME} sources/main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET ${PROJECT_NAME}\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${PROJECT_NAME}> ${PROJECT_SOURCE_DIR}/../../${PROJECT_NAME}\n'
            ')\n'
        )

    def test_recipe_is_not_regenerated_if_up_to_date_files_are_found(self):
        filesystem = self.filesystemMockWithRecipeFiles()
        project = self.deathStarBackend()
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_not_called()
        filesystem.create_file.assert_not_called()

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
        project.sources = ['sources/main.cpp']
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

