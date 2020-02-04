class Plugin(object):
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.sources = []
        self.packages = []
        self.include_directories = []

    def __eq__(self, other):
        return self.name == other.name

    def add_include_directory(self, directory):
        self.include_directories.append(directory)

    def add_package(self, package):
        self.packages.append(package)

    def add_sources(self, sources):
        self.sources.extend(sources)
