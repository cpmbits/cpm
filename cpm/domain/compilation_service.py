from cpm.domain.project.project_descriptor_parser import ParseError


class CompilationService(object):
    def __init__(self, project_loader, cmakelists_builder, project_commands):
        self.project_loader = project_loader
        self.cmakelists_builder = cmakelists_builder
        self.project_commands = project_commands

    def build(self, target_name='default'):
        project = self.project_loader.load('.', target_name)
        self.cmakelists_builder.build(project)
        self.project_commands.build(project)

    def update(self, target_name='default'):
        project = self.project_loader.load('.', target_name)
        self.cmakelists_builder.build(project)

    def clean(self):
        project = self.try_load_project()
        self.project_commands.clean(project)

    def try_load_project(self):
        project = None
        try:
            project = self.project_loader.load('.')
        except ParseError as e:
            print(f'cpm: warning: parsing error while cleaning ({e.message})')
        return project
