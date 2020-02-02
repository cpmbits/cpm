import subprocess

from cpm.domain.compilation_recipes import CompilationRecipe
from cpm.domain.compilation_recipes import cmake
from cpm.domain.compilation_recipes import RECIPES_DIRECTORY

BUILD_DIRECTORY = f'{RECIPES_DIRECTORY}/build'


class BuildRecipe(CompilationRecipe):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem):
        self.filesystem = filesystem

    def generate(self, project):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            self.filesystem.create_directory(BUILD_DIRECTORY)
        self.filesystem.symlink('../../main.cpp', 'recipes/build/main.cpp')
        for package in project.packages:
            self.filesystem.symlink(f'../../{package.path}', f'recipes/build/{package.path}')

        self.filesystem.create_file(
            f'{BUILD_DIRECTORY}/CMakeLists.txt',
            self.build_cmakelists(project)
        )

    def build_cmakelists(self, project):
        return cmake.a_cmake() \
            .minimum_required('3.7') \
            .project(project.name) \
            .include(project.include_directories) \
            .add_executable(project.name, project.sources) \
            .add_custom_command(
                    project.name,
                    'POST_BUILD',
                    f'${{CMAKE_COMMAND}} -E copy $<TARGET_FILE:{project.name}> ${{PROJECT_SOURCE_DIR}}/../../{project.name}') \
            .contents

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


class MacOsBuildRecipe(BuildRecipe):
    CMAKE_COMMAND = '/Applications/CMake.app/Contents/bin/cmake'
