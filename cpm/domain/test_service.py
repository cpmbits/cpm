class TestService(object):
    def __init__(self, project_loader):
        self.project_loader = project_loader

    def run_tests(self, recipe):
        project = self.project_loader.load()
        recipe.generate(project)
        recipe.compile(project)
        recipe.run_tests(project)
