import unittest

from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.project.project import Project, Target, Package


def a_project(name):
    return TestProjectBuilder(name)


class TestCmakelistsBuilder(unittest.TestCase):
    def test_build_cmakelists_from_project(self):
        cmakelists_builder = CMakeListsBuilder()
        project = a_project('Project') \
            .with_target('default') \
            .with_cflags(['-std=c++11']) \
            .with_package('package', ['file.cpp', 'file.c'], ['-DHOLA']) \
            .project

        cmakelists_content = cmakelists_builder.build_contents(project, 'default')

        assert 'cmake_minimum_required (VERSION 3.7)' in cmakelists_content
        assert 'project(Project)' in cmakelists_content
        assert 'add_library(package_object_library OBJECT file.cpp file.c)' in cmakelists_content
        assert 'set_target_properties(package_object_library PROPERTIES COMPILE_FLAGS "-DHOLA")' in cmakelists_content
        assert 'add_executable(Project main.cpp $<TARGET_OBJECTS:package_object_library>)' in cmakelists_content
        assert 'set_target_properties(Project PROPERTIES COMPILE_FLAGS "-std=c++11")' in cmakelists_content
        assert 'include_directories(package)' in cmakelists_content


class TestProjectBuilder:
    def __init__(self, name):
        self.target_name = ''
        self.project = Project(name)

    def with_target(self, target_name):
        self.target_name = target_name
        target = Target(target_name)
        self.project.targets[target_name] = target
        return self

    def with_cflags(self, cflags):
        self.project.targets[self.target_name].cflags = cflags
        return self

    def with_package(self, path, sources, cflags):
        package = Package(path)
        package.sources = sources
        package.cflags = cflags
        self.project.targets[self.target_name].packages.append(package)
        self.project.targets[self.target_name].include_directories.add(path)
        return self
