from dataclasses import dataclass
from dataclasses import field


@dataclass
class Target:
    name: str
    properties: dict


@dataclass
class Package:
    path: str
    sources: list = field(default_factory=list)
    cflags: list = field(default_factory=list)


@dataclass
class LinkOptions:
    flags: list = field(default_factory=list)
    libraries: list = field(default_factory=list)


@dataclass
class ProjectAction(object):
    name: str
    command: str


class Project(object):
    def __init__(self, name):
        self.name = name
        self.version = "0.1"
        self.tests = []
        self.declared_bits = {}
        self.declared_test_bits = {}
        self.bits = []
        self.sources = []
        self.packages = []
        self.compile_flags = []
        self.include_directories = []
        self.link_options = LinkOptions()
        self.actions = []
        self.targets = {}
        self.test_packages = []
        self.test_include_directories = []
        self.test_sources = []

    def add_target(self, target):
        self.targets[target.name] = target

    def add_bit(self, bit):
        self.bits.append(bit)

    def add_sources(self, sources):
        self.sources.extend(sources)

    def add_tests(self, tests):
        self.tests.extend(tests)

    def add_package(self, package):
        self.packages.append(package)

    def add_include_directory(self, directory):
        self.include_directories.append(directory)

    def add_test_package(self, package):
        self.test_packages.append(package)

    def add_test_include_directory(self, directory):
        self.test_include_directories.append(directory)

    def add_test_sources(self, sources):
        self.test_sources.extend(sources)

    def add_library(self, library):
        self.link_options.libraries.append(library)

    def add_action(self, project_action):
        self.actions.append(project_action)

    def add_compile_flags(self, compile_flags):
        self.compile_flags.extend(compile_flags)
