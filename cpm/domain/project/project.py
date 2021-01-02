from dataclasses import dataclass, field

from cpm.domain.project.project_descriptor import ProjectDescriptor


@dataclass
class Package:
    path: str
    sources: list = field(default_factory=list)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)


@dataclass
class Target:
    name: str
    executable: str = ''
    main: str = 'main.cpp'
    image: str = ''
    dockerfile: str = ''
    packages: list = field(default_factory=list)
    include_directories: set = field(default_factory=set)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)
    bits: list = field(default_factory=list)
    test_bits: list = field(default_factory=list)


@dataclass
class Test:
    name: str
    target: Target
    main: str
    packages: list = field(default_factory=list)
    include_directories: set = field(default_factory=set)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)


@dataclass
class Project:
    name: str = ''
    version: str = ''
    description: str = ''
    descriptor: ProjectDescriptor = field(default_factory=ProjectDescriptor)
    targets: dict = field(default_factory=dict)
    tests: list = field(default_factory=list)
    declared_bits: list = field(default_factory=list)
    actions: list = field(default_factory=list)
