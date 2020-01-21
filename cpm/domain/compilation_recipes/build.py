import subprocess

from cpm.domain.compilation_recipes import CompilationRecipe
from cpm.domain.compilation_recipes import RECIPES_DIRECTORY

CMAKE_RECIPE = (
    'cmake_minimum_required (VERSION 3.7)\n'
    'set(PROJECT_NAME {project_name})\n'
    'project(${{PROJECT_NAME}})\n'
    'include_directories(sources)\n'
    'add_executable(${{PROJECT_NAME}} {sources_list})\n'
    'add_custom_command(\n'
    '    TARGET ${{PROJECT_NAME}}\n'
    '    POST_BUILD\n'
    '    COMMAND COMMAND ${{CMAKE_COMMAND}} -E copy $<TARGET_FILE:${{PROJECT_NAME}}> ${{PROJECT_SOURCE_DIR}}/../../${{PROJECT_NAME}}\n'
    ')\n'
)


class BuildRecipe(CompilationRecipe):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem):
        self.filesystem = filesystem

    def generate(self, project):
        self.filesystem.create_directory(self.__recipe_directory())
        self.filesystem.create_file(
            f'{RECIPES_DIRECTORY}/build/CMakeLists.txt',
            CMAKE_RECIPE.format(
                project_name=project.name,
                sources_list=' '.join(project.sources)
            )
        )
        self.filesystem.symlink('../../sources', 'recipes/build/sources')

    def compile(self, project):
        subprocess.run(
            [self.CMAKE_COMMAND, '-G', 'Ninja', '.'],
            cwd=self.__recipe_directory()
        )
        subprocess.run(
            ['ninja', project.name],
            cwd=self.__recipe_directory()
        )

    def __recipe_directory(self):
        return f'{RECIPES_DIRECTORY}/build'


class MacOsXBuildRecipe(BuildRecipe):
    CMAKE_COMMAND = '/Applications/CMake.app/Contents/bin/cmake'
