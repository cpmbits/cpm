class CMakeListsBuilder(object):
    def __init__(self):
        self.contents = ''
        self.object_libraries = []
        self.test_object_libraries = []

    def build(self, project):
        self.build_contents(project)
        with open('CMakeLists.txt', 'w') as cmakelists_file:
            cmakelists_file.write(self.contents)

    def build_contents(self, project):
        self.minimum_required('3.13')
        if project.target.toolchain_prefix:
            self.set_compilers(project.target.toolchain_prefix)
        self.project(project.name)
        for package in self.bit_packages_with_sources(project.target):
            self.object_libraries += self.build_package_recipe(package)
        for package in self.target_packages_with_sources(project.target):
            self.object_libraries += self.build_package_recipe(package)
        self.link_libraries(project.target.libraries)
        self.add_executable(
            project.name,
            [project.target.main],
            self.object_libraries
        )
        self.set_target_properties(project.name, 'COMPILE_FLAGS', self.main_compile_flags(project, project.target.main))
        self.target_link_options(project.name, project.target.ldflags)
        self.include_directories(project.target.include_directories)
        for package in self.test_packages_with_sources(project.test):
            self.test_object_libraries += self.build_package_recipe(package)
        for package in self.bit_packages_with_sources(project.test):
            self.test_object_libraries += self.build_package_recipe(package)
        for test in project.test.test_suites:
            self.add_executable(
                test.name,
                [test.main],
                self.object_libraries + self.test_object_libraries
            )
            self.set_target_properties(test.name, 'COMPILE_FLAGS', self.test_main_compile_flags(project, test.main))
            self.target_link_options(test.name, project.test.ldflags)
            self.target_include_directories(
                test.name,
                project.test.include_directories
                    .union(test.include_directories)
            )
            self.target_link_libraries(test.name, project.test.libraries + test.libraries)
        if project.test.test_suites:
            self.add_custom_target('tests', 'echo ""', [test.name for test in project.test.test_suites])
        return self.contents

    def target_packages_with_sources(self, target):
        return [package for package in target.packages if package.sources]

    def bit_packages_with_sources(self, target):
        return [package for bit in target.bits for package in bit.packages if package.sources]

    def test_packages_with_sources(self, test):
        return [package for package in test.packages if package.sources]

    def build_package_recipe(self, package):
        package_c_library_name = self.object_library_name(package.path + '_c')
        package_cpp_library_name = self.object_library_name(package.path + '_cpp')
        return self.build_package_library_recipe(package, package_c_library_name, package.cflags, '.c') + \
               self.build_package_library_recipe(package, package_cpp_library_name, package.cppflags, '.cpp')

    def build_package_library_recipe(self, package, package_library_name, compile_flags, extension):
        sources = list(filter(lambda s: s.endswith(extension), package.sources))
        if not sources:
            return []
        self.add_object_library(package_library_name, sources)
        self.set_target_properties(package_library_name, 'COMPILE_FLAGS', compile_flags)
        self.target_include_directories(package_library_name, package.include_directories)
        return [f'$<TARGET_OBJECTS:{package_library_name}>']

    def object_library_name(self, package_path):
        return f'{package_path.replace("/", "_")}_object_library'

    def minimum_required(self, version):
        self.contents += f'cmake_minimum_required (VERSION {version})\n'

    def project(self, name):
        self.contents += f'project({name})\n'

    def include_directories(self, directories):
        self.contents += f'include_directories({" ".join(sorted(directories))})\n'

    def set_source_files_properties(self, sources, property, values):
        self.contents += f'set_source_files_properties({" ".join(sources)} PROPERTIES {property} "{" ".join(values)}")\n'

    def add_object_library(self, name, sources):
        self.contents += f'add_library({name} OBJECT {" ".join(sources)})\n'

    def add_static_library(self, name, sources):
        self.contents += f'add_library({name} STATIC {" ".join(sources)})\n'

    def add_executable(self, name, sources, object_libraries=[]):
        self.contents += f'add_executable({name} {" ".join(sources)}'
        for library in object_libraries:
            self.contents += f' {library}'
        self.contents += ')\n'

    def main_compile_flags(self, project, main_filename):
        if main_filename.endswith('.c'):
            return project.target.cflags
        elif main_filename.endswith('.cpp'):
            return project.target.cppflags
        return []

    def test_main_compile_flags(self, project, main_filename):
        if main_filename.endswith('.c'):
            return project.target.cflags + project.test.cflags
        elif main_filename.endswith('.cpp'):
            return project.target.cppflags + project.test.cppflags
        return []

    def set_target_properties(self, target, property, values):
        if values:
            self.contents += f'set_target_properties({target} PROPERTIES {property} "{" ".join(values)}")\n'

    def target_link_options(self, target, values):
        if values:
            self.contents += f'target_link_options({target} PUBLIC "{" ".join(values)}")\n'

    def target_link_libraries(self, target, libraries):
        if libraries:
            self.contents += f'target_link_libraries({target} {" ".join(libraries)})\n'

    def link_libraries(self, libraries):
        if libraries:
            self.contents += f'link_libraries({" ".join(libraries)})\n'

    def target_include_directories(self, target, directories):
        if directories:
            self.contents += f'target_include_directories({target} PUBLIC {" ".join(sorted(directories))})\n'

    def add_custom_target(self, target, command, depends):
        self.contents += f'add_custom_target({target}\n' \
                         f'    COMMAND {command}\n' \
                         f'    DEPENDS {" ".join(depends)}\n' \
                         f')\n'

    def add_custom_command(self, target, when, command):
        self.contents += f'add_custom_command(\n' \
                         f'    TARGET {target}\n' \
                         f'    {when}\n' \
                         f'    COMMAND COMMAND {command}\n' \
                         f')\n'

    def set_compilers(self, toolchain_prefix):
        self.contents += f'set(CMAKE_C_COMPILER {toolchain_prefix}gcc)\n'
        self.contents += f'set(CMAKE_CXX_COMPILER {toolchain_prefix}g++)\n'
