from dataclasses import dataclass, field

from cpm.domain.project.project_descriptor import ProjectDescriptor


@dataclass
class Package:
    path: str
    sources: list = field(default_factory=list)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    include_directories: set = field(default_factory=set)


@dataclass
class Target:
    name: str = 'default'
    executable: str = ''
    main: str = 'main.cpp'
    image: str = ''
    dockerfile: str = ''
    test_image: str = ''
    toolchain_prefix: str = ''
    post_build: list = field(default_factory=list)
    packages: list = field(default_factory=list)
    include_directories: set = field(default_factory=set)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)
    bits: list = field(default_factory=list)


@dataclass
class TestSuite:
    name: str
    main: str
    packages: list = field(default_factory=list)
    include_directories: set = field(default_factory=set)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)


@dataclass
class Test:
    test_suites: list = field(default_factory=list)
    packages: list = field(default_factory=list)
    include_directories: set = field(default_factory=set)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)
    bits: list = field(default_factory=list)


@dataclass
class Project:
    name: str = ''
    version: str = '0.1'
    description: str = ''
    descriptor: ProjectDescriptor = field(default_factory=ProjectDescriptor)
    target: Target = field(default_factory=Test)
    test: Test = field(default_factory=Test)
    declared_bits: list = field(default_factory=list)
    actions: list = field(default_factory=list)
