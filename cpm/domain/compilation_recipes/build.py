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
        self.create_symlinks_to_sources(project)
        self.generate_cmakelists(project)

    def generate_cmakelists(self, project):
        self.filesystem.create_file(
            f'{BUILD_DIRECTORY}/CMakeLists.txt',
            self.build_cmakelists(project)
        )

    def create_symlinks_to_sources(self, project):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            self.filesystem.create_directory(BUILD_DIRECTORY)
        self.filesystem.symlink('../../main.cpp', 'recipes/build/main.cpp')
        for package in project.packages:
            self.filesystem.symlink(f'../../{package.path}', f'recipes/build/{package.path}')
        if project.plugins:
            self.filesystem.symlink('../../plugins', 'recipes/build/plugins')

    def build_cmakelists(self, project):
        cmake_builder = cmake.a_cmake() \
            .minimum_required('3.7') \
            .project(project.name) \
            .include(project.include_directories)
        for package in project.packages:
            if package.cflags:
                cmake_builder.set_source_files_properties(package.sources, 'COMPILE_FLAGS', package.cflags)
        cmake_builder.add_executable(project.name, project.sources)
        if project.link_options.libraries:
            cmake_builder.target_link_libraries(project.name, project.link_options.libraries)
        cmake_builder.add_custom_command(
                    project.name,
                    'POST_BUILD',
                    f'${{CMAKE_COMMAND}} -E copy $<TARGET_FILE:{project.name}> ${{PROJECT_SOURCE_DIR}}/../../{project.name}')

        return cmake_builder.contents

    def compile(self, project):
        subprocess.run(
            [self.CMAKE_COMMAND, '-G', 'Ninja', '.'],
            cwd=BUILD_DIRECTORY
        )
        subprocess.run(
            ['ninja', project.name],
            cwd=BUILD_DIRECTORY
        )

