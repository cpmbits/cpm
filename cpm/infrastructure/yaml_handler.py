import yaml


class YamlHandler:
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def load(self, file_name):
        if not self.filesystem.file_exists(file_name):
            raise FileNotFoundError()
        with open(file_name) as stream:
            return yaml.safe_load(stream)

    def dump(self, file_name, data):
        with open(file_name, 'w') as stream:
            return yaml.dump(data, stream)
