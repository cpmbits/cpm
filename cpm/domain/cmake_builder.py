from collections import OrderedDict


class CMakeBuilder(object):
    def __init__(self):
        self.contents = ''

    def minimum_required(self, version):
        self.contents += f'cmake_minimum_required (VERSION {version})\n'
        return self

    def project(self, name):
        self.contents += f'project({name})\n'
        return self

    def include(self, directories):
        self.contents += f'include_directories({" ".join(self.no_duplicates(directories))})\n'
        return self

    def no_duplicates(self, directories):
        return list(OrderedDict.fromkeys(directories))

    def set_source_files_properties(self, sources, property, values):
        self.contents += f'set_source_files_properties({" ".join(sources)} PROPERTIES {property} "{" ".join(values)}")\n'
        return self

    def add_object_library(self, name, sources):
        self.contents += f'add_library({name} OBJECT {" ".join(sources)})\n'
        return self

    def add_static_library(self, name, sources):
        self.contents += f'add_library({name} STATIC {" ".join(sources)})\n'
        return self

    def add_executable(self, name, sources, object_libraries=[]):
        self.contents += f'add_executable({name} {" ".join(sources)}'
        for library in object_libraries:
            self.contents += f' $<TARGET_OBJECTS:{library}>'
        self.contents += ')\n'
        return self

    def set_target_properties(self, target, property, values):
        self.contents += f'set_target_properties({target} PROPERTIES {property} "{" ".join(values)}")\n'
        return self

    def target_link_libraries(self, target, libraries):
        self.contents += f'target_link_libraries({target} {" ".join(libraries)})\n'
        return self

    def target_include_directories(self, target, directories):
        self.contents += f'target_include_directories({target} PUBLIC {" ".join(directories)})\n'
        return self

    def add_custom_target(self, target, command, depends):
        self.contents += f'add_custom_target({target}\n' \
                         f'    COMMAND {command}"\n' \
                         f'    DEPENDS {" ".join(depends)}\n' \
                         f')\n'
        return self

    def add_custom_command(self, target, when, command):
        self.contents += f'add_custom_command(\n' \
                         f'    TARGET {target}\n' \
                         f'    {when}\n' \
                         f'    COMMAND COMMAND {command}\n' \
                         f')\n'
        return self


def a_cmake():
    return CMakeBuilder()
