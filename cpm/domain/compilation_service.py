import os
import sys
import docker


class CompilationService(object):
    def __init__(self, project_loader, cmakelists_builder, project_commands):
        self.project_loader = project_loader
        self.cmakelists_builder = cmakelists_builder
        self.project_commands = project_commands

    def build(self, target='default'):
        project = self.project_loader.load('.')
        self.cmakelists_builder.build(project, target)
        self.project_commands.build(project, target)

    def update(self, target='default'):
        project = self.project_loader.load('.')
        self.cmakelists_builder.build(project, target)

    def clean(self):
        project = self.project_loader.load('.')
        self.project_commands.clean(project)



