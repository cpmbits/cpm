from dataclasses import dataclass, field


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
    packages: list = field(default_factory=list)
    include_directories: set = field(default_factory=set)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)


@dataclass
class Test:
    name: str
    target: Target
    main: str
    packages: list = field(default_factory=list)
    include_directories: list = field(default_factory=list)
    cflags: list = field(default_factory=list)
    cppflags: list = field(default_factory=list)
    ldflags: list = field(default_factory=list)


@dataclass
class Project:
    name: str = ''
    version: str = ''
    description: str = ''
    targets: dict = field(default_factory=dict)
    tests: list = field(default_factory=list)
