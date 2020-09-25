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


class CompileRecipe(object):
    def __init__(self):
        self.declared_bits = {}
        self.bits = []
        self.sources = []
        self.packages = []
        self.compile_flags = []
        self.include_directories = []
        self.link_options = LinkOptions()

    def add_bit(self, bit):
        self.bits.append(bit)

    def add_package(self, package):
        self.packages.append(package)

    def add_sources(self, sources):
        self.sources.extend(sources)

    def add_include_directory(self, directory):
        self.include_directories.append(directory)

    def add_library(self, library):
        self.link_options.libraries.append(library)

    def add_compile_flags(self, compile_flags):
        self.compile_flags.extend(compile_flags)


class Project(object):
    def __init__(self, name):
        self.name = name
        self.version = "0.1"
        self.tests = []
        self.test = CompileRecipe()
        self.build = CompileRecipe()
        self.actions = []
        self.targets = {}

    def add_target(self, target):
        self.targets[target.name] = target

    def add_build_recipe(self, recipe):
        self.build = recipe

    def add_test_recipe(self, recipe):
        self.test = recipe

    def add_tests(self, tests):
        self.tests.extend(tests)

    def add_action(self, project_action):
        self.actions.append(project_action)

