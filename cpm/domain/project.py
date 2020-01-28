from dataclasses import dataclass

PROJECT_ROOT_FILE = 'project.yaml'


@dataclass
class Target:
    name: str
    properties: dict


@dataclass
class Package:
    path: str


class Project(object):
    def __init__(self, name):
        self.name = name
        self.sources = []
        self.tests = []
        self.plugins = []
        self.packages = []
        self.targets = {}

    def add_target(self, target):
        self.targets[target.name] = target

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def add_sources(self, source):
        self.sources.extend(source)

    def add_tests(self, tests):
        self.tests.extend(tests)

    def add_packages(self, packages):
        self.packages = packages
