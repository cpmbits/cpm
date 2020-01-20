PROJECT_ROOT_FILE = 'project.yaml'


class Target(object):
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties


class Project(object):
    def __init__(self, name):
        self.name = name
        self.targets = {}
        self.sources = []

    def add_target(self, target):
        self.targets[target.name] = target

    def add_sources(self, source):
        self.sources.extend(source)

