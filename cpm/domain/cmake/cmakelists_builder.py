class CMakeListsBuilder(object):
    def __init__(self):
        self.contents = ''

    def build(self, project, target_name):
        self.build_contents(project, target_name)
        with open('CMakeLists.txt', 'w') as cmakelists_file:
            cmakelists_file.write(self.contents)

    def build_contents(self, project, target_name):
        target = project.targets[target_name]
        self.minimum_required('3.7')
        self.project(project.name)
        for package in self.bit_packages_with_sources(target):
            self.build_package_recipe(package)
        for package in self.target_packages_with_sources(target):
            self.build_package_recipe(package)
        self.link_libraries(target.libraries)
        self.add_executable(
            project.name,
            [target.main],
            [self.object_library_name(package.path) for package in self.target_packages_with_sources(target)] +
            [self.object_library_name(package.path) for package in self.bit_packages_with_sources(target)]
        )
        self.set_target_properties(project.name, 'COMPILE_FLAGS', target.cflags)
        self.include_directories(target.include_directories)
        for test in project.tests:
            for package in self.test_packages_with_sources(test):
                self.build_package_recipe(package)
            self.add_executable(
                test.name,
                [test.main],
                [self.object_library_name(package.path) for package in self.target_packages_with_sources(target)] +
                [self.object_library_name(package.path) for package in self.bit_packages_with_sources(target)] +
                [self.object_library_name(package.path) for package in self.test_packages_with_sources(test)]
            )
            self.set_target_properties(project.name, 'COMPILE_FLAGS', test.cflags)
            self.target_include_directories(test.name, test.include_directories)
            self.target_link_libraries(test.name, test.libraries)
        if project.tests:
            self.add_custom_target('tests', 'echo "> Done', [test.name for test in project.tests])
        return self.contents

    def target_packages_with_sources(self, target):
        return [package for package in target.packages if package.sources]

    def bit_packages_with_sources(self, target):
        return [package for bit in target.bits for package in bit.packages if package.sources]

    def test_packages_with_sources(self, test):
        return [package for package in test.packages if package.sources]

    def build_package_recipe(self, package):
        package_library_name = self.object_library_name(package.path)
        self.add_object_library(package_library_name, package.sources)
        self.set_target_properties(package_library_name, 'COMPILE_FLAGS', package.cflags)

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
            self.contents += f' $<TARGET_OBJECTS:{library}>'
        self.contents += ')\n'

    def set_target_properties(self, target, property, values):
        if values:
            self.contents += f'set_target_properties({target} PROPERTIES {property} "{" ".join(values)}")\n'

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
                         f'    COMMAND {command}"\n' \
                         f'    DEPENDS {" ".join(depends)}\n' \
                         f')\n'

    def add_custom_command(self, target, when, command):
        self.contents += f'add_custom_command(\n' \
                         f'    TARGET {target}\n' \
                         f'    {when}\n' \
                         f'    COMMAND COMMAND {command}\n' \
                         f')\n'
