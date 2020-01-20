import unittest
import mock

from cpm.domain.compilation_recipes.build import BuildRecipe


class TestBuildRecipe(unittest.TestCase):
    def test_instantiation(self):
        filesystem = mock.MagicMock()
        BuildRecipe(filesystem)

    def test_recipe_creates_recipes_directory(self):
        filesystem = mock.MagicMock()
        project = mock.MagicMock()
        project.name = 'DeathStarBackend'
        project.sources = ['sources/main.cpp']
        build_recipe = BuildRecipe(filesystem)

        build_recipe.generate(project)

        filesystem.create_directory.assert_called_once_with('recipes/build')
        filesystem.create_file.assert_called_once_with(
            'recipes/build/CMakeLists.txt',

            'set(PROJECT_NAME DeathStarBackend)\n'
            'project(${NAME})\n'
            'add_executable(${NAME} sources/main.cpp)\n'
            'add_custom_command(\n'
            '    TARGET ${NAME}\n'
            '    POST_BUILD\n'
            '    COMMAND COMMAND ${CMAKE_COMMAND} - E copy $ <TARGET_FILE:${NAME}> ${PROJECT_SOURCE_DIR}/${NAME}\n'
            ')\n'
        )
