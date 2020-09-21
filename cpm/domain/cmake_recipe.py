import subprocess
import signal

from cpm.domain import cmake_builder

CMAKELISTS = 'CMakeLists.txt'
BUILD_DIRECTORY = f'build'


class CMakeRecipe(object):
    CMAKE_COMMAND = 'cmake'

    def __init__(self, filesystem, compile_bits_as_libraries=False):
        self.filesystem = filesystem
        self.compile_bits_as_libraries = compile_bits_as_libraries
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
        builder = cmake_builder.a_cmake() \
            .minimum_required('3.7') \
            .project(project.name) \
            .include(project.include_directories)

        self.__generate_build_rules(builder, project)

        self.__generate_test_rules(builder, project)

        return builder.contents

    def __generate_test_rules(self, builder, project):
        self.test_executables = [test_file.split('/')[-1].split('.')[0] for test_file in project.tests]
        if self.test_executables:
            sources_without_main = self._sources_without_main(project)
            if sources_without_main:
                project_object_library = project.name + '_object_library'
                builder.add_object_library(project_object_library, sources_without_main)
                object_libraries = [project_object_library]
            else:
                object_libraries = []
            for executable, test_file in zip(self.test_executables, project.tests):
                builder.add_executable(executable, [test_file] + project.test_sources, object_libraries) \
                    .set_target_properties(executable, 'COMPILE_FLAGS', ['-std=c++11', '-g'])
                bits_with_sources = list(filter(lambda p: p.sources, project.bits))
                link_libraries = [bit.name for bit in bits_with_sources] + project.link_options.libraries
                if link_libraries:
                    builder.target_link_libraries(executable, link_libraries)
                if project.test_include_directories:
                    builder.target_include_directories(executable, project.test_include_directories)
            builder.add_custom_target('tests', 'echo "> Done', self.test_executables)

    def __generate_build_rules(self, builder, project):
        for package in project.packages:
            if package.cflags:
                builder.set_source_files_properties(package.sources, 'COMPILE_FLAGS', package.cflags)
        for bit in project.bits:
            self.__generate_bit_build_rules(builder, bit)
        builder.add_executable(project.name, project.sources)
        if project.compile_flags:
            builder.set_target_properties(project.name, 'COMPILE_FLAGS', project.compile_flags)
        self.__generate_link_libraries_rule(builder, project)

    def __generate_link_libraries_rule(self, builder, project):
        bits_with_sources = list(filter(lambda p: p.sources, project.bits))
        if project.link_options.libraries or bits_with_sources:
            link_libraries = [bit.name for bit in bits_with_sources] + project.link_options.libraries
            builder.target_link_libraries(project.name, link_libraries)

    def __generate_bit_build_rules(self, builder, bit):
        if bit.sources:
            builder.add_static_library(bit.name, bit.sources)
        for package in bit.packages:
            if package.cflags:
                builder.set_source_files_properties(package.sources, 'COMPILE_FLAGS', package.cflags)

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
        self.run_compile_command('ninja', 'tests')

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
