class TestService(object):
    def __init__(self, project_loader, cmakelists_builder, project_commands):
        self.project_loader = project_loader
        self.cmakelists_builder = cmakelists_builder
        self.project_commands = project_commands

    def run_tests(self, files_or_dirs, target):
        project = self.project_loader.load('.')
        if not project.tests:
            raise NoTestsFound()
        self.cmakelists_builder.build(project, target)
        self.project_commands.build_tests(project, target, files_or_dirs)
        self.project_commands.run_tests(project, target, files_or_dirs)


class NoTestsFound(RuntimeError):
    pass
