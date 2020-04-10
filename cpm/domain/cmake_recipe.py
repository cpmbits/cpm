import subprocess
import signal

from cpm.domain import cmake

CMAKELISTS = 'CMakeLists.txt'
BUILD_DIRECTORY = f'build'


class CMakeRecipe(object):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.test_executables = []

    def generate(self, project):
        self.create_build_directory(project)
        self.generate_cmakelists(project)

    def generate_cmakelists(self, project):
        self.filesystem.create_file(
            CMAKELISTS,
            self.build_cmakelists(project)
        )

    def create_build_directory(self, project):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            self.filesystem.create_directory(BUILD_DIRECTORY)

    def build_cmakelists(self, project):
        cmake_builder = cmake.a_cmake() \
            .minimum_required('3.7') \
            .project(project.name) \
            .include(project.include_directories)

        self.__generate_build_rules(cmake_builder, project)

        self.__generate_test_rules(cmake_builder, project)

        return cmake_builder.contents

    def __generate_test_rules(self, cmake_builder, project):
        self.test_executables = [test_file.split('/')[-1].split('.')[0] for test_file in project.tests]

        if self.test_executables:
            sources_without_main = self._sources_without_main(project)
            if sources_without_main:
                project_object_library = project.name + '_object_library'
                cmake_builder.add_object_library(project_object_library, sources_without_main)
                object_libraries = [project_object_library]
            else:
                object_libraries = []
            for executable, test_file in zip(self.test_executables, project.tests):
                cmake_builder.add_executable(executable, [test_file], object_libraries) \
                    .set_target_properties(executable, 'COMPILE_FLAGS', ['-std=c++11', '-g'])
                if project.link_options.libraries:
                    cmake_builder.target_link_libraries(executable, project.link_options.libraries)
            cmake_builder.add_custom_target('test', 'echo "> Done', self.test_executables)

    def __generate_build_rules(self, cmake_builder, project):
        for package in project.packages:
            if package.cflags:
                cmake_builder.set_source_files_properties(package.sources, 'COMPILE_FLAGS', package.cflags)
        cmake_builder.add_executable(project.name, project.sources)
        if project.link_options.libraries:
            cmake_builder.target_link_libraries(project.name, project.link_options.libraries)

    def _sources_without_main(self, project):
        return list(filter(lambda x: x != "main.cpp", project.sources))

    def build(self, project):
        self.run_compile_command(self.CMAKE_COMMAND, '-G', 'Ninja', '..')
        self.run_compile_command('ninja', project.name)

    def run_compile_command(self, *args):
        result = subprocess.run([*args], cwd=BUILD_DIRECTORY)
        if result.returncode != 0:
            raise CompilationError()

    def build_tests(self):
        self.run_compile_command(self.CMAKE_COMMAND, '-G', 'Ninja', '..')
        self.run_compile_command('ninja', 'test')

    def run_all_tests(self):
        self.run_tests(self.test_executables)

    def run_tests(self, executables):
        test_results = [self.run_test(executable) for executable in executables]
        if any(result.returncode != 0 for result in test_results):
            raise TestsFailed('tests failed')

    def run_test(self, executable):
        result = subprocess.run(
            [f'./{executable}'],
            cwd=BUILD_DIRECTORY
        )
        if result.returncode < 0:
            print(f'{executable} failed with {result.returncode} ({signal.Signals(-result.returncode).name})')
        return result

    def clean(self):
        if not self.filesystem.directory_exists(BUILD_DIRECTORY):
            return
        subprocess.run(
            ['ninja', 'clean'],
            cwd=BUILD_DIRECTORY
        )
        self.filesystem.delete_file(CMAKELISTS)
        self.filesystem.remove_directory(BUILD_DIRECTORY)


class TestsFailed(RuntimeError):
    pass


class CompilationError(RuntimeError):
    pass
