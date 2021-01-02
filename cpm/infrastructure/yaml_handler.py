import yaml
from cpm.infrastructure import filesystem


def load(file_name):
    if not filesystem.file_exists(file_name):
        raise FileNotFoundError()
    with open(file_name) as stream:
        return yaml.safe_load(stream)


def dump(file_name, data):
    with open(file_name, 'w') as stream:
        return yaml.dump(data, stream)
