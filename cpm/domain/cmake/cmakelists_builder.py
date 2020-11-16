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
        self.add_executable(project.name, [target.main])
        return self.contents

    def minimum_required(self, version):
        self.contents += f'cmake_minimum_required (VERSION {version})\n'

    def project(self, name):
        self.contents += f'project({name})\n'

    def include(self, directories):
        self.contents += f'include_directories({" ".join(directories)})\n'

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
        self.contents += f'set_target_properties({target} PROPERTIES {property} "{" ".join(values)}")\n'

    def target_link_libraries(self, target, libraries):
        self.contents += f'target_link_libraries({target} {" ".join(libraries)})\n'

    def target_include_directories(self, target, directories):
        self.contents += f'target_include_directories({target} PUBLIC {" ".join(directories)})\n'

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
