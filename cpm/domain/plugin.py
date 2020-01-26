class Plugin(object):
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties

    def __eq__(self, other):
        return self.name == other.name
