from dataclasses import dataclass
from dataclasses import field

PROJECT_ROOT_FILE = 'project.yaml'


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
        self.plugins = []
        self.sources = []
        self.packages = []
        self.include_directories = []
        self.link_options = LinkOptions()
        self.actions = []
        self.targets = {}

    def add_target(self, target):
        self.targets[target.name] = target

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def add_sources(self, sources):
        self.sources.extend(sources)

    def add_tests(self, tests):
        self.tests.extend(tests)

    def add_package(self, package):
        self.packages.append(package)

    def add_include_directory(self, directory):
        self.include_directories.append(directory)

    def add_library(self, library):
        self.link_options.libraries.append(library)

    def add_action(self, project_action):
        self.actions.append(project_action)