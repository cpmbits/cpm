import ast

from collections import namedtuple
from dataclasses import dataclass, field


YamlLine = namedtuple('YamlLine', ['indentation', 'raw', 'key', 'value', 'type', 'comment'])


@dataclass
class YamlNode:
    key: str
    parent: object = None
    line: str = ''
    comment: str = ''
    line_number: int = 0
    indentation: int = 0


@dataclass
class KeyValuePair(YamlNode):
    value: str = ''

    def as_dict(self):
        return {
            self.key: self.value
        }

    def dump(self):
        return f'{" "*self.indentation}{self.key}: {self.value}\n'


@dataclass
class ScalarNode(YamlNode):
    value: str = ''

    def as_dict(self):
        return self.value

    def dump(self):
        return self.value


@dataclass
class SequenceNode(YamlNode):
    nodes: list = field(default_factory=list)

    def as_dict(self):
        value = [node.as_dict() for node in self.nodes]
        return {
            self.key: value
        }

    def dump(self):
        value = f'{" "*self.indentation}{self.key}:\n'
        for node in self.nodes:
            value += f'{" "*node.indentation}- {node.dump()}\n'
        return value


@dataclass
class FlowSequenceNode(YamlNode):
    values: list = field(default_factory=list)

    def as_dict(self):
        return {
            self.key: self.values
        }

    def dump(self):
        value = f'{" "*self.indentation}{self.key}: ['
        value += ','.join([f"'{v}" for v in self.values]) + ']\n'
        return value


@dataclass
class MapNode(YamlNode):
    nodes: list = field(default_factory=list)

    def as_dict(self):
        value = {}
        for node in self.nodes:
            value.update(node.as_dict())
        return {
            self.key: value if value else None
        }

    def dump(self):
        value = f'{" "*self.indentation}{self.key}:\n'
        for node in self.nodes:
            value += node.dump()
        return value


@dataclass
class YamlDocument:
    raw: str = ''
    raw_lines: list = field(default_factory=list)
    lines: list = field(default_factory=list)
    nodes: list = field(default_factory=list)
    parent: object = None
    indentation: int = 0

    def as_dict(self):
        value = {}
        for node in self.nodes:
            value.update(node.as_dict())
        return value

    def dump(self):
        value = ''
        for node in self.nodes:
            value += node.dump()
        return value

    def __setitem__(self, key, value):
        for node in self.nodes:
            if node.key == key:
                node.value = value


class YamlParser:
    def __init__(self):
        self.yaml_document = YamlDocument()
        self.parent_node = self.yaml_document
        self.current_indentation = 0
        self.current_line = 0
        self.last_node = None

    def parse(self, payload):
        self.yaml_document.raw = payload
        self.yaml_document.raw_lines = payload.splitlines()
        for number, line in enumerate(self.yaml_document.raw_lines):
            # try:
            self.parse_line(number+1, line)
            # except:
            #     print(f'error parsing file at {number+1}')

    def parse_line(self, number, line):
        if not line.strip():
            return

        self.current_line = number
        indentation = self.indentation(line)
        tokens = list(map(lambda token: token.strip(), line.split(':', maxsplit=1)))

        node = self.__parse_node(tokens)

        if node:
            node.line_number = number
            node.line = line
            node.indentation = indentation

            self.update_parent_node(node)

            self.parent_node.nodes.append(node)
            self.last_node = node

    def indentation(self, line):
        return len(line) - len(line.lstrip(' '))

    def update_parent_node(self, node):
        if self.last_node:
            if type(node) == ScalarNode:
                if type(self.last_node) != ScalarNode:
                    self.parent_node = self.last_node
                self.parent_node.__class__ = SequenceNode
            else:
                if node.indentation > self.last_node.indentation:
                    self.parent_node = self.last_node
                elif node.indentation < self.last_node.indentation or type(self.last_node) == ScalarNode:
                    while node.indentation <= self.parent_node.indentation and self.parent_node != self.yaml_document:
                        self.parent_node = self.parent_node.parent
        node.parent = self.parent_node

    def __parse_node(self, tokens):
        if len(tokens) == 1:
            if tokens[0].startswith('- '):
                value = self.__eval(tokens[0].split('-', maxsplit=1)[1].strip())
                node = ScalarNode(key='', value=value)
            else:
                value = self.__eval(tokens[0].strip())
                if type(self.parent_node) == SequenceNode and self.last_node.parent == self.parent_node:
                    self.last_node.value = f'{self.last_node.value} {value}'
                node = None
        else:
            key = self.__eval(tokens[0])
            value = self.__eval(tokens[1])
            if value is None:
                node = MapNode(key=key)
            else:
                if type(value) == list:
                    node = FlowSequenceNode(key=key, values=value)
                else:
                    node = KeyValuePair(key=key, value=value)
        return node

    def __eval(self, value):
        if value == '':
            return None
        try:
            evaluated = ast.literal_eval(value)
        except:
            evaluated = value
        return None if evaluated == 'null' else evaluated


def parse_file(filename):
    with open(filename, 'r') as stream:
        raw = stream.read()
    return parse(raw)


def parse(payload):
    parser = YamlParser()
    parser.parse(payload)
    return parser.yaml_document
