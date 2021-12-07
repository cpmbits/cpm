from pathlib import Path

from ruamel.yaml import YAML, RoundTripConstructor


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
        path = Path(node.value)
        self.files.append(path)
        return yaml.load(path)

    def included_files(self):
        return self.files + [f for p in self.child_parsers for f in p.included_files()]


class YamlParser(YAML):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Constructor = CpmConstructor

    def included_files(self):
        return self.constructor.included_files()
