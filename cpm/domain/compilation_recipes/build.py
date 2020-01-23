import subprocess

from cpm.domain.compilation_recipes import CompilationRecipe
from cpm.domain.compilation_recipes import RECIPES_DIRECTORY

BUILD_DIRECTORY = f'{RECIPES_DIRECTORY}/build'
CMAKE_RECIPE = (
    '''cmake_minimum_required (VERSION 3.7)
set(PROJECT_NAME {project_name})
project(${{PROJECT_NAME}})
include_directories(sources)
add_executable(${{PROJECT_NAME}} {sources_list})
add_custom_command(
    TARGET ${{PROJECT_NAME}}
    POST_BUILD
    COMMAND COMMAND ${{CMAKE_COMMAND}} -E copy $<TARGET_FILE:${{PROJECT_NAME}}> ${{PROJECT_SOURCE_DIR}}/../../${{PROJECT_NAME}}
)
'''
)


class BuildRecipe(CompilationRecipe):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem):
        self.filesystem = filesystem

    def generate(self, project):
        if self._recipe_files_up_to_date():
            return
        self.filesystem.create_directory(BUILD_DIRECTORY)
        self.filesystem.create_file(
            f'{BUILD_DIRECTORY}/CMakeLists.txt',
            CMAKE_RECIPE.format(
                project_name=project.name,
                sources_list=' '.join(project.sources)
            )
        )
        self.filesystem.symlink('../../sources', 'recipes/build/sources')

    def _recipe_files_up_to_date(self):
        return self.filesystem.directory_exists(BUILD_DIRECTORY) and \
               self.filesystem.file_exists(f'{BUILD_DIRECTORY}/CMakeLists.txt')

    def compile(self, project):
        subprocess.run(
            [self.CMAKE_COMMAND, '-G', 'Ninja', '.'],
            cwd=BUILD_DIRECTORY
        )
        subprocess.run(
            ['ninja', project.name],
            cwd=BUILD_DIRECTORY
        )


class MacOsXBuildRecipe(BuildRecipe):
    CMAKE_COMMAND = '/Applications/CMake.app/Contents/bin/cmake'
