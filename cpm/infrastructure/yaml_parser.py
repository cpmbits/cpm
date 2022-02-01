from pathlib import Path

from ruamel.yaml import YAML, RoundTripConstructor
from ruamel.yaml.nodes import SequenceNode, MappingNode

from cpm.infrastructure import filesystem

class CpmConstructor(RoundTripConstructor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_constructor(u'!include', self.include)
        self.files = []
        self.child_parsers = []

    def include(self, loader, node):
        y = loader.loader
        yaml = YamlParser(typ=y.typ, pure=y.pure)
        self.child_parsers.append(yaml)
        yaml.composer.anchors = loader.composer.anchors
        path = Path(filesystem.join(filesystem.path_to(self.parsing_file), node.value))
        self.files.append(path)
        return yaml.load_from(path)

    def construct_object(self, node, deep=False):
        data = super().construct_object(node, deep)
        if isinstance(node, MappingNode) or isinstance(node, SequenceNode):
            setattr(data, 'parsing_file', self.parsing_file)
        return data

    def set_parsing_file(self, parsing_file):
        setattr(self, 'parsing_file', parsing_file)

    def included_files(self):
        return self.files + [f for p in self.child_parsers for f in p.included_files()]


class YamlParser(YAML):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Constructor = CpmConstructor

    def load_from(self, stream):
        setattr(self, 'parsing_file', stream)
        self.constructor.set_parsing_file(stream.name)
        return self.load(stream)

    def included_files(self):
        return self.constructor.included_files()


def load(path):
    yaml = YamlParser()
    return yaml.load_from(Path(path))


def dump(data, path):
    yaml = YamlParser(typ='rt')
    yaml.dump(data, Path(path))
