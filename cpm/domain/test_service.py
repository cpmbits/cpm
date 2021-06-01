class TestService(object):
    def __init__(self, project_loader, cmakelists_builder, project_commands):
        self.project_loader = project_loader
        self.cmakelists_builder = cmakelists_builder
        self.project_commands = project_commands

    def run_tests(self, files_or_dirs, target_name, test_args=()):
        project = self.project_loader.load('.', target_name)
        if not project.test.test_suites:
            raise NoTestsFound()
        self.cmakelists_builder.build(project)
        self.project_commands.build_tests(project, files_or_dirs)
        self.project_commands.run_tests(project, files_or_dirs, test_args)


class NoTestsFound(RuntimeError):
    pass
