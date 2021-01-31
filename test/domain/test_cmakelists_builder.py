import unittest

from cpm.domain.cmake.cmakelists_builder import CMakeListsBuilder
from cpm.domain.project.project import Project, Target, Package, Test, TestSuite


def a_project(name):
    return TestProjectBuilder(name)


class TestCmakelistsBuilder(unittest.TestCase):
    def test_build_cmakelists_from_project(self):
        cmakelists_builder = CMakeListsBuilder()
        project = a_project('Project') \
            .with_target('default') \
            .with_cflags(['-std=c++11']) \
            .with_libraries(['pthread']) \
            .with_package('package', ['file.cpp', 'file.c'], ['-DHOLA']) \
            .with_package('spdlog', [], []) \
            .with_test('test_case') \
            .with_test_package('bits/cest', [], []) \
            .with_test_package('bits/mock', ['bits/mock/mock.cpp'], []) \
            .sort_include_directories() \
            .project

        cmakelists_content = cmakelists_builder.build_contents(project)

        assert 'cmake_minimum_required (VERSION 3.7)' in cmakelists_content
        assert 'project(Project)' in cmakelists_content
        assert 'add_library(package_object_library OBJECT file.cpp file.c)' in cmakelists_content
        assert 'set_target_properties(package_object_library PROPERTIES COMPILE_FLAGS "-DHOLA")' in cmakelists_content
        assert 'link_libraries(pthread)' in cmakelists_content
        assert 'add_executable(Project main.cpp $<TARGET_OBJECTS:package_object_library>)' in cmakelists_content
        assert 'set_target_properties(Project PROPERTIES COMPILE_FLAGS "-std=c++11")' in cmakelists_content
        assert 'include_directories(package spdlog)' in cmakelists_content
        assert 'add_library(bits_mock_object_library OBJECT bits/mock/mock.cpp)' in cmakelists_content
        assert 'add_executable(test_case test_case.cpp $<TARGET_OBJECTS:package_object_library> $<TARGET_OBJECTS:bits_mock_object_library>)' in cmakelists_content
        assert 'target_include_directories(test_case PUBLIC bits/cest bits/mock)' in cmakelists_content
        assert ('add_custom_target(tests\n'
               '    COMMAND echo "> Done"\n'
               '    DEPENDS test_case\n'
               ')\n') in cmakelists_content


class TestProjectBuilder:
    def __init__(self, name):
        self.target_name = ''
        self.target = None
        self.project = Project(name)

    def with_target(self, target_name):
        self.target_name = target_name
        self.target = Target(target_name)
        self.project.target = self.target
        return self

    def with_cflags(self, cflags):
        self.project.target.cflags = cflags
        return self

    def with_libraries(self, libraries):
        self.project.target.libraries = libraries
        return self

    def with_package(self, path, sources, cflags):
        package = Package(path)
        package.sources = sources
        package.cflags = cflags
        self.project.target.packages.append(package)
        self.project.target.include_directories.add(path)
        return self

    def with_test(self, test_name):
        test = TestSuite(test_name, f'{test_name}.cpp')
        self.project.test.test_suites.append(test)
        return self

    def with_test_package(self, path, sources, cflags):
        package = Package(path)
        package.sources = sources
        package.cflags = cflags
        self.project.test.packages.append(package)
        self.project.test.include_directories.add(path)
        return self

    def sort_include_directories(self):
        self.target.include_directories = set(sorted(list(self.target.include_directories)))
        self.project.test.include_directories = set(sorted(list(self.project.test.include_directories)))
        for test in self.project.test.test_suites:
            test.include_directories = set(sorted(list(test.include_directories)))
        return self
