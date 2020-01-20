import unittest
import mock

from cpm.domain.compilation_recipes.build import BuildRecipe
from cpm.domain.compilation_recipes.build import MacOsXBuildRecipe


class TestBuildRecipe(unittest.TestCase):
    def test_instantiation(self):
        filesystem = mock.MagicMock()
        BuildRecipe(filesystem)

    def test_recipe_creates_recipes_directory_and_symlinks_sources(self):
        filesystem = mock.MagicMock()
        project = mock.MagicMock()
        project.name = 'DeathStarBackend'
        project.sources = ['sources/main.cpp']
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/build')
        filesystem.create_file.assert_called_once_with(
            'recipes/build/CMakeLists.txt',

            'cmake_minimum_required (VERSION 3.7)\n'
            'set(PROJECT_NAME DeathStarBackend)\n'
            'project(${PROJECT_NAME})\n'
            'add_executable(${PROJECT_NAME} sources/main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET ${PROJECT_NAME}\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${PROJECT_NAME}> ${PROJECT_SOURCE_DIR}/../../${PROJECT_NAME}\n'
            ')\n'
        )
        filesystem.symlink.assert_called_once_with('../../sources', 'recipes/build/sources')

    @mock.patch('subprocess.run')
    def test_recipe_compiles_with_cmake_and_ninja(self, subprocess_run):
        filesystem = mock.MagicMock()
        project = mock.MagicMock()
        project.name = 'DeathStarBackend'
        build_recipe = MacOsXBuildRecipe(filesystem)

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

