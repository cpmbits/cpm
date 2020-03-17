import os

from cpm.api.result import Result


class ProjectActionRunner(object):
    def __init__(self, name, command):
        self.name = name
        self.command = command

    def __eq__(self, other):
        return self.name == other.name

    def execute(self, argv):
        return_code = os.system(self.command)
        return Result(return_code, f'finished "{self.name}"')
